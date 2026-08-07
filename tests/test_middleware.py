import base64
import json
import logging

from fastmcp import Client, FastMCP
from mcp import McpError
from pydantic import BaseModel, ValidationError

from opensvc_collector_mcp.audit import AUDIT_LOGGER_NAME, McpToolCallAuditEvent
from opensvc_collector_mcp.auth.basic import CollectorBasicAuthMiddleware
from opensvc_collector_mcp.auth.middleware import (
    CollectorToolAuthorizationMiddleware,
    ToolSchemaValidationErrorMiddleware,
)


def test_basic_auth_parser_returns_collector_credentials():
    encoded = base64.b64encode(b"collector-user:collector-password").decode()

    credentials = CollectorBasicAuthMiddleware._parse_basic_auth(f"Basic {encoded}")

    assert credentials.username == "collector-user"
    assert credentials.password == "collector-password"


def test_basic_auth_parser_rejects_invalid_header():
    try:
        CollectorBasicAuthMiddleware._parse_basic_auth("Bearer token")
    except McpError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected invalid authorization header to raise")

    assert "Expected Basic Authorization header" in message


async def test_internal_validation_error_is_not_reported_as_invalid_tool_arguments():
    class InnerModel(BaseModel):
        value: int

    server = FastMCP("internal-validation-test")

    @server.tool(name="internal_validation_tool")
    async def internal_validation_tool(name: str) -> dict[str, str]:
        try:
            InnerModel.model_validate({"value": "not-an-int"})
        except ValidationError as exc:
            raise exc
        return {"name": name}

    server.add_middleware(ToolSchemaValidationErrorMiddleware(server))

    async with Client(server) as client:
        try:
            await client.call_tool("internal_validation_tool", {"name": "ok"})
        except Exception as exc:
            message = str(exc)
        else:
            raise AssertionError("expected internal validation error to raise")

    assert "Invalid tool arguments" not in message
    assert "expected_input_schema" not in message
    assert "InnerModel" in message
    assert "value" in message


async def test_tool_middleware_does_not_authorize_from_effect_tags():
    server = FastMCP("collector-authorization-test")

    @server.tool(name="read_tool", tags={"read"})
    async def read_tool() -> dict[str, str]:
        return {"status": "read"}

    @server.tool(name="write_tool", tags={"write:nodes"})
    async def write_tool() -> dict[str, str]:
        return {"status": "written"}

    @server.tool(name="untagged_tool")
    async def untagged_tool() -> dict[str, str]:
        return {"status": "untagged"}

    @server.tool(name="mixed_tag_tool", tags={"read", "write:nodes"})
    async def mixed_tag_tool() -> dict[str, str]:
        return {"status": "mixed"}

    server.add_middleware(CollectorToolAuthorizationMiddleware(server))

    async with Client(server) as client:
        read_result = await client.call_tool("read_tool", {})
        write_result = await client.call_tool("write_tool", {})
        untagged_result = await client.call_tool("untagged_tool", {})
        mixed_result = await client.call_tool("mixed_tag_tool", {})

    assert read_result.structured_content == {"status": "read"}
    assert write_result.structured_content == {"status": "written"}
    assert untagged_result.structured_content == {"status": "untagged"}
    assert mixed_result.structured_content == {"status": "mixed"}


async def test_tool_middleware_audits_direct_call_without_rbac_fields(caplog):
    caplog.set_level(logging.INFO, logger=AUDIT_LOGGER_NAME)
    server = FastMCP("tool-audit-test")

    @server.tool(name="write_tool", tags={"nodes", "write:nodes"})
    async def write_tool() -> dict[str, str]:
        return {"status": "changed"}

    server.add_middleware(CollectorToolAuthorizationMiddleware(server))

    async with Client(server) as client:
        result = await client.call_tool("write_tool", {})

    assert result.structured_content == {"status": "changed"}
    event = _single_audit_event(caplog)
    _assert_strict_tool_call_event(event)
    assert event["event"] == "mcp.tool_call"
    assert event["request_id"] is None
    assert event["user"] is None
    assert event["client_tool"] == "write_tool"
    assert event["target_tool"] == "write_tool"
    assert event["decision"] == "allowed"
    assert event["reason"] == "authorization_delegated_to_collector"
    assert isinstance(event["duration_ms"], int)
    assert event["status"] == "success"
    assert event["error_type"] is None
    assert event["error_message"] is None
    assert event["required_tag"] is None
    assert event["required_groups"] == []
    assert event["user_groups"] is None
    assert event["tool_tags"] == ["nodes", "write:nodes"]


async def test_tool_middleware_audits_tool_execution_error(caplog):
    caplog.set_level(logging.INFO, logger=AUDIT_LOGGER_NAME)
    server = FastMCP("tool-audit-test")

    @server.tool(name="read_tool", tags={"read"})
    async def read_tool() -> dict[str, str]:
        raise RuntimeError("tool failed")

    server.add_middleware(CollectorToolAuthorizationMiddleware(server))

    async with Client(server) as client:
        try:
            await client.call_tool("read_tool", {})
        except Exception as exc:
            message = str(exc)
        else:
            raise AssertionError("expected read tool failure to raise")

    assert "tool failed" in message
    event = _single_audit_event(caplog)
    _assert_strict_tool_call_event(event)
    assert event["client_tool"] == "read_tool"
    assert event["target_tool"] == "read_tool"
    assert event["decision"] == "allowed"
    assert event["reason"] == "authorization_delegated_to_collector"
    assert event["status"] == "error"
    assert event["error_type"] == "RuntimeError"
    assert event["error_message"] == "tool failed"
    assert event["required_tag"] is None
    assert event["required_groups"] == []
    assert event["user_groups"] is None
    assert event["tool_tags"] == ["read"]


async def test_tool_middleware_audits_public_search_tool(caplog):
    caplog.set_level(logging.INFO, logger=AUDIT_LOGGER_NAME)
    server = FastMCP("tool-audit-test")

    @server.tool(name="search_tools")
    async def search_tools(query: str) -> dict[str, str]:
        return {"query": query}

    server.add_middleware(CollectorToolAuthorizationMiddleware(server))

    async with Client(server) as client:
        result = await client.call_tool("search_tools", {"query": "node detail"})

    assert result.structured_content == {"query": "node detail"}
    event = _single_audit_event(caplog)
    _assert_strict_tool_call_event(event)
    assert event["client_tool"] == "search_tools"
    assert event["target_tool"] is None
    assert event["decision"] == "allowed"
    assert event["reason"] == "public_tool"
    assert event["status"] == "success"
    assert event["required_tag"] is None
    assert event["required_groups"] == []
    assert event["user_groups"] is None
    assert event["tool_tags"] is None


async def test_tool_middleware_includes_ai_request_id(monkeypatch, caplog):
    caplog.set_level(logging.INFO, logger=AUDIT_LOGGER_NAME)
    monkeypatch.setattr(
        "opensvc_collector_mcp.auth.middleware.get_http_headers",
        lambda include=None: {"x-opensvc-ai-request-id": "ai_test"},
    )
    server = FastMCP("tool-audit-test")

    @server.tool(name="search_tools")
    async def search_tools(query: str) -> dict[str, str]:
        return {"query": query}

    server.add_middleware(CollectorToolAuthorizationMiddleware(server))

    async with Client(server) as client:
        result = await client.call_tool("search_tools", {"query": "node detail"})

    assert result.structured_content == {"query": "node detail"}
    event = _single_audit_event(caplog)
    _assert_strict_tool_call_event(event)
    assert event["request_id"] == "ai_test"


async def test_tool_middleware_audits_call_tool_target_without_authorizing(caplog):
    caplog.set_level(logging.INFO, logger=AUDIT_LOGGER_NAME)
    server = FastMCP("tool-audit-test")

    @server.tool(name="write_tool", tags={"nodes", "write:nodes"})
    async def write_tool() -> dict[str, str]:
        return {"status": "changed"}

    @server.tool(name="call_tool")
    async def call_tool(name: str, arguments: dict) -> dict[str, str]:
        return {"target": name, "status": "called"}

    server.add_middleware(CollectorToolAuthorizationMiddleware(server))

    async with Client(server) as client:
        result = await client.call_tool(
            "call_tool",
            {"name": "write_tool", "arguments": {}},
        )

    assert result.structured_content == {"target": "write_tool", "status": "called"}
    event = _single_audit_event(caplog)
    _assert_strict_tool_call_event(event)
    assert event["client_tool"] == "call_tool"
    assert event["target_tool"] == "write_tool"
    assert event["decision"] == "allowed"
    assert event["reason"] == "authorization_delegated_to_collector"
    assert event["status"] == "success"
    assert event["required_tag"] is None
    assert event["required_groups"] == []
    assert event["user_groups"] is None
    assert event["tool_tags"] == ["nodes", "write:nodes"]


def _single_audit_event(caplog) -> dict:
    events = [
        json.loads(record.message)
        for record in caplog.records
        if record.name == AUDIT_LOGGER_NAME
    ]
    assert len(events) == 1
    return events[0]


def _assert_strict_tool_call_event(event: dict) -> None:
    assert set(event) == set(McpToolCallAuditEvent.model_fields)
    McpToolCallAuditEvent.model_validate(event)

import base64
import json
import logging

from fastmcp import Client, FastMCP
from mcp import McpError
from pydantic import BaseModel, ValidationError

from opensvc_collector_mcp.audit import AUDIT_LOGGER_NAME
from opensvc_collector_mcp.middleware import (
    CollectorBasicAuthMiddleware,
    CollectorReadToolAuthorizationMiddleware,
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


async def test_read_tool_authorization_allows_read_tagged_tool(caplog):
    caplog.set_level(logging.INFO, logger=AUDIT_LOGGER_NAME)
    server = FastMCP("read-authorization-test")

    @server.tool(name="read_tool", tags={"read"})
    async def read_tool() -> dict[str, str]:
        return {"status": "ok"}

    server.add_middleware(
        CollectorReadToolAuthorizationMiddleware(
            server,
            group_roles_loader=lambda: async_group_roles({"Everybody"}),
        )
    )

    async with Client(server) as client:
        result = await client.call_tool("read_tool", {})

    assert result.structured_content == {"status": "ok"}
    event = _single_audit_event(caplog)
    assert event["event"] == "mcp.tool_authorization"
    assert event["client_tool"] == "read_tool"
    assert event["target_tool"] == "read_tool"
    assert event["decision"] == "allowed"
    assert event["required_tag"] == "read"
    assert event["required_groups"] == ["Everybody", "Manager"]
    assert event["user_groups"] == ["Everybody"]
    assert event["tool_tags"] == ["read"]


async def test_read_tool_authorization_denies_non_read_tool():
    server = FastMCP("read-authorization-test")

    @server.tool(name="write_tool", tags={"write:nodes"})
    async def write_tool() -> dict[str, str]:
        return {"status": "changed"}

    server.add_middleware(
        CollectorReadToolAuthorizationMiddleware(
            server,
            group_roles_loader=lambda: async_group_roles({"Everybody"}),
        )
    )

    async with Client(server) as client:
        try:
            await client.call_tool("write_tool", {})
        except Exception as exc:
            message = str(exc)
        else:
            raise AssertionError("expected non-read tool to be denied")

    assert "Unauthorized tool" in message
    assert "write_tool" in message
    assert "required_tag" in message
    assert "read" in message


async def test_read_tool_authorization_denies_read_tool_without_required_group(caplog):
    caplog.set_level(logging.INFO, logger=AUDIT_LOGGER_NAME)
    server = FastMCP("read-authorization-test")

    @server.tool(name="read_tool", tags={"read"})
    async def read_tool() -> dict[str, str]:
        return {"status": "ok"}

    server.add_middleware(
        CollectorReadToolAuthorizationMiddleware(
            server,
            group_roles_loader=lambda: async_group_roles({"TeamA"}),
        )
    )

    async with Client(server) as client:
        try:
            await client.call_tool("read_tool", {})
        except Exception as exc:
            message = str(exc)
        else:
            raise AssertionError("expected read tool to be denied without group")

    assert "Unauthorized tool" in message
    assert "read_tool" in message
    assert "required_groups" in message
    assert "Everybody" in message
    assert "Manager" in message
    assert "TeamA" in message
    event = _single_audit_event(caplog)
    assert event["event"] == "mcp.tool_authorization"
    assert event["client_tool"] == "read_tool"
    assert event["target_tool"] == "read_tool"
    assert event["decision"] == "denied"
    assert event["reason"] == "missing_required_group"
    assert event["required_tag"] == "read"
    assert event["required_groups"] == ["Everybody", "Manager"]
    assert event["user_groups"] == ["TeamA"]
    assert event["tool_tags"] == ["read"]


async def test_read_tool_authorization_audits_public_search_tool(caplog):
    caplog.set_level(logging.INFO, logger=AUDIT_LOGGER_NAME)
    server = FastMCP("read-authorization-test")

    @server.tool(name="search_tools")
    async def search_tools(query: str) -> dict[str, str]:
        return {"query": query}

    server.add_middleware(
        CollectorReadToolAuthorizationMiddleware(
            server,
            group_roles_loader=lambda: async_group_roles(set()),
        )
    )

    async with Client(server) as client:
        result = await client.call_tool("search_tools", {"query": "node detail"})

    assert result.structured_content == {"query": "node detail"}
    event = _single_audit_event(caplog)
    assert event["event"] == "mcp.tool_authorization"
    assert event["client_tool"] == "search_tools"
    assert event["target_tool"] is None
    assert event["decision"] == "allowed"
    assert event["reason"] == "public_tool"
    assert event["required_tag"] == "read"
    assert event["required_groups"] == ["Everybody", "Manager"]
    assert "user_groups" not in event
    assert "tool_tags" not in event


async def test_read_tool_authorization_audits_call_tool_target(caplog):
    caplog.set_level(logging.INFO, logger=AUDIT_LOGGER_NAME)
    server = FastMCP("read-authorization-test")

    @server.tool(name="read_tool", tags={"read"})
    async def read_tool() -> dict[str, str]:
        return {"status": "ok"}

    @server.tool(name="call_tool")
    async def call_tool(name: str, arguments: dict) -> dict[str, str]:
        return {"target": name, "status": "called"}

    server.add_middleware(
        CollectorReadToolAuthorizationMiddleware(
            server,
            group_roles_loader=lambda: async_group_roles({"Manager"}),
        )
    )

    async with Client(server) as client:
        result = await client.call_tool(
            "call_tool",
            {"name": "read_tool", "arguments": {}},
        )

    assert result.structured_content == {"target": "read_tool", "status": "called"}
    event = _single_audit_event(caplog)
    assert event["event"] == "mcp.tool_authorization"
    assert event["client_tool"] == "call_tool"
    assert event["target_tool"] == "read_tool"
    assert event["decision"] == "allowed"
    assert event["required_tag"] == "read"
    assert event["required_groups"] == ["Everybody", "Manager"]
    assert event["user_groups"] == ["Manager"]
    assert event["tool_tags"] == ["read"]


async def test_read_tool_authorization_checks_call_tool_target():
    server = FastMCP("read-authorization-test")

    @server.tool(name="write_tool", tags={"write:nodes"})
    async def write_tool() -> dict[str, str]:
        return {"status": "changed"}

    @server.tool(name="call_tool")
    async def call_tool(name: str, arguments: dict) -> dict[str, str]:
        return {"target": name, "status": "called"}

    server.add_middleware(
        CollectorReadToolAuthorizationMiddleware(
            server,
            group_roles_loader=lambda: async_group_roles({"Manager"}),
        )
    )

    async with Client(server) as client:
        try:
            await client.call_tool(
                "call_tool",
                {"name": "write_tool", "arguments": {}},
            )
        except Exception as exc:
            message = str(exc)
        else:
            raise AssertionError("expected non-read proxy target to be denied")

    assert "Unauthorized tool" in message
    assert "write_tool" in message


async def async_group_roles(group_roles: set[str]) -> set[str]:
    return group_roles


def _single_audit_event(caplog) -> dict:
    events = [
        json.loads(record.message)
        for record in caplog.records
        if record.name == AUDIT_LOGGER_NAME
    ]
    assert len(events) == 1
    return events[0]

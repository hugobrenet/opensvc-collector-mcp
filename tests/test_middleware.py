import base64

from fastmcp import Client, FastMCP
from mcp import McpError
from pydantic import BaseModel, ValidationError

from opensvc_collector_mcp.middleware import (
    CollectorBasicAuthMiddleware,
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

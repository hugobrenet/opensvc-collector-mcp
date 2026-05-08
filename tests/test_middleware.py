from fastmcp import Client, FastMCP
from pydantic import BaseModel, ValidationError

from opensvc_collector_mcp.middleware import ToolSchemaValidationErrorMiddleware


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

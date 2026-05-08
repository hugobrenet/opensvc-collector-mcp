import json
from typing import Any

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext
from fastmcp.tools import ToolResult
from mcp import types as mt
from pydantic import ValidationError


class ToolSchemaValidationErrorMiddleware(Middleware):
    """Return the called tool input schema when argument validation fails."""

    def __init__(self, server: FastMCP) -> None:
        self.server = server

    @staticmethod
    def _is_tool_argument_validation_error(
        tool_name: str, exc: ValidationError
    ) -> bool:
        return getattr(exc, "title", None) == f"call[{tool_name}]"

    async def on_call_tool(
        self,
        context: MiddlewareContext[mt.CallToolRequestParams],
        call_next: CallNext[mt.CallToolRequestParams, ToolResult],
    ) -> ToolResult:
        try:
            return await call_next(context)
        except ValidationError as exc:
            tool_name = context.message.name
            if not self._is_tool_argument_validation_error(tool_name, exc):
                raise

            tool = await self.server.get_tool(tool_name)
            expected_input_schema: dict[str, Any] | None = None
            if tool is not None:
                expected_input_schema = tool.parameters

            payload = {
                "error": "Invalid tool arguments",
                "tool": tool_name,
                "validation_errors": exc.errors(),
                "expected_input_schema": expected_input_schema,
                "hint": "Retry with arguments matching expected_input_schema.",
            }
            raise ToolError(json.dumps(payload, ensure_ascii=False, default=str)) from exc

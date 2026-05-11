import base64
import binascii
import json
from typing import Any

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext
from fastmcp.tools import ToolResult
from mcp import McpError
from mcp import types as mt
from pydantic import ValidationError

from opensvc_collector_mcp.client import (
    CollectorCredentials,
    reset_collector_credentials,
    set_collector_credentials,
    validate_collector_credentials,
)


class CollectorBasicAuthMiddleware(Middleware):
    """Validate MCP HTTP Basic Auth against the OpenSVC Collector."""

    @staticmethod
    def _unauthorized(message: str) -> McpError:
        return McpError(
            mt.ErrorData(
                code=-32600,
                message=message,
            )
        )

    @classmethod
    def _parse_basic_auth(cls, authorization: str | None) -> CollectorCredentials:
        if not authorization:
            raise cls._unauthorized("Missing Authorization header")

        scheme, separator, token = authorization.partition(" ")
        if separator != " " or scheme.lower() != "basic" or not token:
            raise cls._unauthorized("Expected Basic Authorization header")

        try:
            decoded = base64.b64decode(token, validate=True).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError) as exc:
            raise cls._unauthorized("Invalid Basic Authorization header") from exc

        username, separator, password = decoded.partition(":")
        if separator != ":" or not username:
            raise cls._unauthorized("Invalid Basic Authorization credentials")

        return CollectorCredentials(username=username, password=password)

    async def on_request(
        self,
        context: MiddlewareContext[Any],
        call_next: CallNext[Any, Any],
    ) -> Any:
        headers = get_http_headers(include={"authorization"})
        credentials = self._parse_basic_auth(headers.get("authorization"))
        if not await validate_collector_credentials(credentials):
            raise self._unauthorized("Invalid Collector credentials")

        token = set_collector_credentials(credentials)
        try:
            return await call_next(context)
        finally:
            reset_collector_credentials(token)


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

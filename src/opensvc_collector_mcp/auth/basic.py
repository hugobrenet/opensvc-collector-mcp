import base64
import binascii
from typing import Any

from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext
from mcp import McpError
from mcp import types as mt

from opensvc_collector_mcp.auth.context import (
    CollectorCredentials,
    reset_collector_credentials,
    set_collector_credentials,
)
from opensvc_collector_mcp.client import validate_collector_credentials


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

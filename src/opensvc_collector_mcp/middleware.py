import base64
import binascii
import json
from collections.abc import Awaitable, Callable
from contextvars import ContextVar
from typing import Any

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext
from fastmcp.tools import ToolResult
from mcp import McpError
from mcp import types as mt
from pydantic import ValidationError

from opensvc_collector_mcp.audit import log_tool_authorization_audit
from opensvc_collector_mcp.client import (
    CollectorCredentials,
    get_collector_credentials,
    get_collector_group_roles,
    reset_collector_credentials,
    set_collector_credentials,
    validate_collector_credentials,
)

_SKIP_NESTED_AUTHORIZATION_AUDIT: ContextVar[bool] = ContextVar(
    "skip_nested_authorization_audit",
    default=False,
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


class CollectorReadToolAuthorizationMiddleware(Middleware):
    """Allow authenticated users to execute only read-tagged Collector tools."""

    def __init__(
        self,
        server: FastMCP,
        *,
        read_tag: str = "read",
        read_groups: set[str] | None = None,
        call_tool_name: str = "call_tool",
        public_tool_names: set[str] | None = None,
        group_roles_loader: Callable[[], Awaitable[set[str]]] | None = None,
    ) -> None:
        self.server = server
        self.read_tag = read_tag
        self.read_groups = read_groups or {"Everybody", "Manager"}
        self.call_tool_name = call_tool_name
        self.public_tool_names = public_tool_names or {"search_tools"}
        self.group_roles_loader = group_roles_loader or get_collector_group_roles

    @staticmethod
    def _tool_arguments(
        context: MiddlewareContext[mt.CallToolRequestParams],
    ) -> dict[str, Any]:
        arguments = context.message.arguments
        if isinstance(arguments, dict):
            return arguments
        return {}

    def _target_tool_name(
        self,
        context: MiddlewareContext[mt.CallToolRequestParams],
    ) -> str | None:
        if context.message.name != self.call_tool_name:
            return context.message.name

        name = self._tool_arguments(context).get("name")
        if isinstance(name, str) and name:
            return name
        return None

    def _unauthorized_tool(
        self,
        tool_name: str,
        tags: set[str],
        *,
        group_roles: set[str] | None = None,
    ) -> ToolError:
        payload = {
            "error": "Unauthorized tool",
            "tool": tool_name,
            "required_tag": self.read_tag,
            "required_groups": sorted(self.read_groups),
            "tags": sorted(tags),
            "user_groups": sorted(group_roles) if group_roles is not None else None,
            "hint": (
                "Only read-tagged Collector tools are allowed for users in "
                "the required Collector groups."
            ),
        }
        return ToolError(json.dumps(payload, ensure_ascii=False, default=str))

    @staticmethod
    def _collector_username() -> str | None:
        credentials = get_collector_credentials()
        if credentials is None:
            return None
        return credentials.username

    def _log_authorization_decision(
        self,
        context: MiddlewareContext[mt.CallToolRequestParams],
        *,
        target_tool_name: str | None,
        tags: set[str] | None,
        decision: str,
        reason: str | None = None,
        group_roles: set[str] | None = None,
    ) -> None:
        if _SKIP_NESTED_AUTHORIZATION_AUDIT.get():
            return
        log_tool_authorization_audit(
            user=self._collector_username(),
            client_tool=context.message.name,
            target_tool=target_tool_name,
            decision=decision,
            reason=reason,
            required_tag=self.read_tag,
            required_groups=self.read_groups,
            user_groups=group_roles,
            tool_tags=tags,
        )

    async def on_call_tool(
        self,
        context: MiddlewareContext[mt.CallToolRequestParams],
        call_next: CallNext[mt.CallToolRequestParams, ToolResult],
    ) -> ToolResult:
        if context.message.name in self.public_tool_names:
            self._log_authorization_decision(
                context,
                target_tool_name=None,
                tags=None,
                decision="allowed",
                reason="public_tool",
            )
            return await call_next(context)

        target_tool_name = self._target_tool_name(context)
        if target_tool_name is None:
            return await call_next(context)

        target_tool = await self.server.get_tool(target_tool_name)
        if target_tool is None:
            return await call_next(context)

        tags = set(target_tool.tags or set())
        if self.read_tag not in tags:
            self._log_authorization_decision(
                context,
                target_tool_name=target_tool_name,
                tags=tags,
                decision="denied",
                reason="missing_required_tag",
            )
            raise self._unauthorized_tool(target_tool_name, tags)

        group_roles = await self.group_roles_loader()
        if not self.read_groups & group_roles:
            self._log_authorization_decision(
                context,
                target_tool_name=target_tool_name,
                tags=tags,
                decision="denied",
                reason="missing_required_group",
                group_roles=group_roles,
            )
            raise self._unauthorized_tool(
                target_tool_name,
                tags,
                group_roles=group_roles,
            )

        self._log_authorization_decision(
            context,
            target_tool_name=target_tool_name,
            tags=tags,
            decision="allowed",
            group_roles=group_roles,
        )
        if context.message.name != self.call_tool_name:
            return await call_next(context)

        token = _SKIP_NESTED_AUTHORIZATION_AUDIT.set(True)
        try:
            return await call_next(context)
        finally:
            _SKIP_NESTED_AUTHORIZATION_AUDIT.reset(token)


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

import json
from collections.abc import Awaitable, Callable
from contextvars import ContextVar
from time import perf_counter
from typing import Any

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext
from fastmcp.tools import ToolResult
from mcp import types as mt
from pydantic import ValidationError

from opensvc_collector_mcp.audit import log_tool_call_audit
from opensvc_collector_mcp.auth.context import get_collector_credentials
from opensvc_collector_mcp.auth.rbac import (
    DEFAULT_TOOL_AUTHORIZATION_POLICY,
    READ_AUTHORIZATION_TAG,
    ToolAuthorizationDecision,
    ToolAuthorizationRequirement,
    authorize_tool,
)
from opensvc_collector_mcp.client import get_collector_group_roles

_SKIP_NESTED_AUTHORIZATION_AUDIT: ContextVar[bool] = ContextVar(
    "skip_nested_authorization_audit",
    default=False,
)
AI_REQUEST_ID_HEADER = "x-opensvc-ai-request-id"


class CollectorToolAuthorizationMiddleware(Middleware):
    """Authorize authenticated Collector tool calls from MCP tags."""

    def __init__(
        self,
        server: FastMCP,
        *,
        authorization_policy: dict[str, set[str]] | None = None,
        call_tool_name: str = "call_tool",
        public_tool_names: set[str] | None = None,
        group_roles_loader: Callable[[], Awaitable[set[str]]] | None = None,
    ) -> None:
        self.server = server
        self.authorization_policy = (
            authorization_policy or DEFAULT_TOOL_AUTHORIZATION_POLICY
        )
        self.call_tool_name = call_tool_name
        self.public_tool_names = public_tool_names or {"search_tools"}
        self.group_roles_loader = group_roles_loader or get_collector_group_roles

    @property
    def public_tool_requirement(self) -> ToolAuthorizationRequirement:
        return ToolAuthorizationRequirement(
            tag=READ_AUTHORIZATION_TAG,
            groups=self.authorization_policy[READ_AUTHORIZATION_TAG],
        )

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
        decision: ToolAuthorizationDecision,
    ) -> ToolError:
        payload = {
            "error": "Unauthorized tool",
            "tool": tool_name,
            "reason": decision.reason,
            "required_tag": (
                decision.requirement.tag if decision.requirement is not None else None
            ),
            "required_groups": (
                sorted(decision.requirement.groups)
                if decision.requirement is not None
                else []
            ),
            "authorization_tags": sorted(decision.authorization_tags),
            "tags": sorted(decision.tool_tags),
            "user_groups": (
                sorted(decision.user_groups)
                if decision.user_groups is not None
                else None
            ),
            "hint": (
                "Collector tool execution requires exactly one known authorization "
                "tag and membership in one of the required Collector groups."
            ),
        }
        return ToolError(json.dumps(payload, ensure_ascii=False, default=str))

    @staticmethod
    def _collector_username() -> str | None:
        credentials = get_collector_credentials()
        if credentials is None:
            return None
        return credentials.username

    @staticmethod
    def _ai_request_id() -> str | None:
        headers = get_http_headers(include={AI_REQUEST_ID_HEADER})
        request_id = headers.get(AI_REQUEST_ID_HEADER)
        if not isinstance(request_id, str) or not request_id:
            return None
        return request_id

    def _log_authorization_decision(
        self,
        context: MiddlewareContext[mt.CallToolRequestParams],
        *,
        target_tool_name: str | None,
        tags: set[str] | None,
        decision: str,
        reason: str | None,
        duration_ms: int,
        status: str,
        error: Exception | None,
        requirement: ToolAuthorizationRequirement | None,
        group_roles: set[str] | None,
    ) -> None:
        if _SKIP_NESTED_AUTHORIZATION_AUDIT.get():
            return
        log_tool_call_audit(
            user=self._collector_username(),
            client_tool=context.message.name,
            target_tool=target_tool_name,
            decision=decision,
            reason=reason,
            duration_ms=duration_ms,
            status=status,
            error_type=type(error).__name__ if error is not None else None,
            error_message=str(error) if error is not None else None,
            required_tag=requirement.tag if requirement is not None else None,
            required_groups=requirement.groups if requirement is not None else set(),
            user_groups=group_roles,
            tool_tags=tags,
            request_id=self._ai_request_id(),
        )

    @staticmethod
    def _duration_ms(started_at: float) -> int:
        return int(round((perf_counter() - started_at) * 1000))

    @staticmethod
    def _audit_error(error: Exception | None) -> Exception | None:
        if error is None:
            return None
        current = error
        while current.__cause__ is not None:
            current = current.__cause__
        return current

    async def _call_next_with_audit(
        self,
        context: MiddlewareContext[mt.CallToolRequestParams],
        call_next: CallNext[mt.CallToolRequestParams, ToolResult],
        *,
        started_at: float,
        target_tool_name: str | None,
        tags: set[str] | None,
        reason: str | None,
        requirement: ToolAuthorizationRequirement | None,
        group_roles: set[str] | None,
        suppress_nested_audit: bool = False,
    ) -> ToolResult:
        token = None
        try:
            if suppress_nested_audit:
                token = _SKIP_NESTED_AUTHORIZATION_AUDIT.set(True)
            result = await call_next(context)
        except Exception as exc:
            if token is not None:
                _SKIP_NESTED_AUTHORIZATION_AUDIT.reset(token)
            audit_error = self._audit_error(exc)
            self._log_authorization_decision(
                context,
                target_tool_name=target_tool_name,
                tags=tags,
                decision="allowed",
                reason=reason,
                duration_ms=self._duration_ms(started_at),
                status="error",
                error=audit_error,
                requirement=requirement,
                group_roles=group_roles,
            )
            raise

        if token is not None:
            _SKIP_NESTED_AUTHORIZATION_AUDIT.reset(token)
        self._log_authorization_decision(
            context,
            target_tool_name=target_tool_name,
            tags=tags,
            decision="allowed",
            reason=reason,
            duration_ms=self._duration_ms(started_at),
            status="success",
            error=None,
            requirement=requirement,
            group_roles=group_roles,
        )
        return result

    async def on_call_tool(
        self,
        context: MiddlewareContext[mt.CallToolRequestParams],
        call_next: CallNext[mt.CallToolRequestParams, ToolResult],
    ) -> ToolResult:
        started_at = perf_counter()
        if context.message.name in self.public_tool_names:
            return await self._call_next_with_audit(
                context,
                call_next,
                started_at=started_at,
                target_tool_name=None,
                tags=None,
                reason="public_tool",
                requirement=self.public_tool_requirement,
                group_roles=None,
            )

        target_tool_name = self._target_tool_name(context)
        if target_tool_name is None:
            return await call_next(context)

        target_tool = await self.server.get_tool(target_tool_name)
        if target_tool is None:
            return await call_next(context)

        tags = set(target_tool.tags or set())
        decision = authorize_tool(
            tool_tags=tags,
            user_groups=None,
            authorization_policy=self.authorization_policy,
        )
        if decision.requirement is None:
            self._log_authorization_decision(
                context,
                target_tool_name=target_tool_name,
                tags=tags,
                decision="denied",
                reason=decision.reason,
                duration_ms=self._duration_ms(started_at),
                status="denied",
                error=None,
                requirement=None,
                group_roles=None,
            )
            raise self._unauthorized_tool(target_tool_name, decision)

        group_roles = await self.group_roles_loader()
        decision = authorize_tool(
            tool_tags=tags,
            user_groups=group_roles,
            authorization_policy=self.authorization_policy,
        )
        if not decision.allowed:
            self._log_authorization_decision(
                context,
                target_tool_name=target_tool_name,
                tags=tags,
                decision="denied",
                reason=decision.reason,
                duration_ms=self._duration_ms(started_at),
                status="denied",
                error=None,
                requirement=decision.requirement,
                group_roles=group_roles,
            )
            raise self._unauthorized_tool(target_tool_name, decision)

        if context.message.name != self.call_tool_name:
            return await self._call_next_with_audit(
                context,
                call_next,
                started_at=started_at,
                target_tool_name=target_tool_name,
                tags=tags,
                reason=None,
                requirement=decision.requirement,
                group_roles=group_roles,
            )

        return await self._call_next_with_audit(
            context,
            call_next,
            started_at=started_at,
            target_tool_name=target_tool_name,
            tags=tags,
            reason=None,
            requirement=decision.requirement,
            group_roles=group_roles,
            suppress_nested_audit=True,
        )


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

import logging
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


AUDIT_LOGGER_NAME = "opensvc_collector_mcp.audit"

_logger = logging.getLogger(AUDIT_LOGGER_NAME)
_logger.setLevel(logging.INFO)


class McpToolCallAuditEvent(BaseModel):
    """Strict JSON contract for MCP tool call audit logs."""

    model_config = ConfigDict(extra="forbid")

    event: Literal["mcp.tool_call"] = "mcp.tool_call"
    request_id: str | None
    user: str | None
    client_tool: str
    target_tool: str | None
    decision: Literal["allowed", "denied"]
    reason: str | None
    duration_ms: int = Field(ge=0)
    status: Literal["success", "denied", "error"]
    error_type: str | None
    error_message: str | None
    required_tag: str | None
    required_groups: list[str]
    user_groups: list[str] | None
    tool_tags: list[str] | None


def log_tool_call_audit(
    *,
    request_id: str | None,
    user: str | None,
    client_tool: str,
    target_tool: str | None,
    decision: str,
    reason: str | None,
    duration_ms: int,
    status: str,
    error_type: str | None,
    error_message: str | None,
    required_tag: str | None,
    required_groups: set[str],
    user_groups: set[str] | None,
    tool_tags: set[str] | None,
) -> None:
    """Emit a compact JSON audit event for an MCP tool call attempt."""
    event = McpToolCallAuditEvent(
        request_id=request_id,
        user=user,
        client_tool=client_tool,
        target_tool=target_tool,
        decision=decision,
        reason=reason,
        duration_ms=duration_ms,
        status=status,
        error_type=error_type,
        error_message=error_message,
        required_tag=required_tag,
        required_groups=sorted(required_groups),
        user_groups=sorted(user_groups) if user_groups is not None else None,
        tool_tags=sorted(tool_tags) if tool_tags is not None else None,
    )

    _logger.info(event.model_dump_json())

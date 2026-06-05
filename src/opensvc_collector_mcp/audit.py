import json
import logging
from typing import Any


AUDIT_LOGGER_NAME = "opensvc_collector_mcp.audit"

_logger = logging.getLogger(AUDIT_LOGGER_NAME)
_logger.setLevel(logging.INFO)


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
    required_tag: str | None,
    required_groups: set[str],
    user_groups: set[str] | None,
    tool_tags: set[str] | None,
) -> None:
    """Emit a compact JSON audit event for an MCP tool call attempt."""
    event: dict[str, Any] = {
        "event": "mcp.tool_call",
        "request_id": request_id,
        "user": user,
        "client_tool": client_tool,
        "target_tool": target_tool,
        "decision": decision,
        "reason": reason,
        "duration_ms": duration_ms,
        "status": status,
        "required_tag": required_tag,
        "required_groups": sorted(required_groups),
        "user_groups": sorted(user_groups) if user_groups is not None else None,
        "tool_tags": sorted(tool_tags) if tool_tags is not None else None,
    }

    _logger.info(json.dumps(event, ensure_ascii=False, default=str))

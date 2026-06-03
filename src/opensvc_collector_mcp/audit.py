import json
import logging
from datetime import UTC, datetime
from typing import Any


AUDIT_LOGGER_NAME = "opensvc_collector_mcp.audit"

_logger = logging.getLogger(AUDIT_LOGGER_NAME)
_logger.setLevel(logging.INFO)


def log_tool_authorization_audit(
    *,
    user: str | None,
    client_tool: str,
    target_tool: str | None,
    decision: str,
    reason: str | None = None,
    required_tag: str | None = None,
    required_groups: set[str] | None = None,
    user_groups: set[str] | None = None,
    tool_tags: set[str] | None = None,
) -> None:
    """Emit a compact JSON audit event for MCP tool authorization decisions."""
    event: dict[str, Any] = {
        "timestamp": datetime.now(UTC).isoformat(),
        "event": "mcp.tool_authorization",
        "user": user,
        "client_tool": client_tool,
        "target_tool": target_tool,
        "decision": decision,
    }
    if reason is not None:
        event["reason"] = reason
    if required_tag is not None:
        event["required_tag"] = required_tag
    if required_groups is not None:
        event["required_groups"] = sorted(required_groups)
    if user_groups is not None:
        event["user_groups"] = sorted(user_groups)
    if tool_tags is not None:
        event["tool_tags"] = sorted(tool_tags)

    _logger.info(json.dumps(event, ensure_ascii=False, default=str))

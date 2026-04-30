from datetime import datetime
from typing import Any

from .inventory import get_node


async def get_node_health(nodename: str) -> dict[str, Any]:
    response = await get_node(nodename)
    data = response.get("data", [])
    if not data:
        return {
            "overall": "unknown",
            "severity": "unknown",
            "node": {"nodename": nodename},
            "issues": [
                {
                    "severity": "unknown",
                    "field": "nodename",
                    "message": "Node was not found in the Collector response.",
                }
            ],
            "signals": {},
        }

    node = data[0]
    issues = _node_health_issues(node)
    severity = _highest_issue_severity(issues)
    return {
        "overall": _node_health_overall(severity),
        "severity": severity,
        "node": {
            "nodename": node.get("nodename"),
            "status": node.get("status"),
            "asset_env": node.get("asset_env"),
            "node_env": node.get("node_env"),
            "app": node.get("app"),
            "loc_city": node.get("loc_city"),
        },
        "issues": issues,
        "signals": {
            "status": node.get("status"),
            "last_comm": node.get("last_comm"),
            "updated": node.get("updated"),
            "last_boot": node.get("last_boot"),
            "maintenance_end": node.get("maintenance_end"),
            "node_frozen": node.get("node_frozen"),
            "node_frozen_at": node.get("node_frozen_at"),
            "snooze_till": node.get("snooze_till"),
            "hw_obs_warn_date": node.get("hw_obs_warn_date"),
            "hw_obs_alert_date": node.get("hw_obs_alert_date"),
            "os_obs_warn_date": node.get("os_obs_warn_date"),
            "os_obs_alert_date": node.get("os_obs_alert_date"),
            "warranty_end": node.get("warranty_end"),
        },
    }


def _node_health_issues(node: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    status = str(node.get("status") or "").lower()
    if status == "down":
        issues.append(
            {
                "severity": "critical",
                "field": "status",
                "message": "Node status is down.",
            }
        )
    elif status == "warn":
        issues.append(
            {
                "severity": "warning",
                "field": "status",
                "message": "Node status is warn.",
            }
        )
    elif not status:
        issues.append(
            {
                "severity": "unknown",
                "field": "status",
                "message": "Node status is missing.",
            }
        )

    for field in ("hw_obs_alert_date", "os_obs_alert_date"):
        if node.get(field):
            issues.append(
                {
                    "severity": "critical",
                    "field": field,
                    "message": f"Collector alert date is set for {field}.",
                }
            )

    for field in ("hw_obs_warn_date", "os_obs_warn_date"):
        if node.get(field):
            issues.append(
                {
                    "severity": "warning",
                    "field": field,
                    "message": f"Collector warning date is set for {field}.",
                }
            )

    if _truthy_node_value(node.get("node_frozen")):
        issues.append(
            {
                "severity": "warning",
                "field": "node_frozen",
                "message": "Node is frozen.",
            }
        )

    now = datetime.now()
    maintenance_end = _parse_collector_datetime(node.get("maintenance_end"))
    if maintenance_end and maintenance_end > now:
        issues.append(
            {
                "severity": "info",
                "field": "maintenance_end",
                "message": "Node is currently in a maintenance window.",
            }
        )

    snooze_till = _parse_collector_datetime(node.get("snooze_till"))
    if snooze_till and snooze_till > now:
        issues.append(
            {
                "severity": "info",
                "field": "snooze_till",
                "message": "Node alerts are currently snoozed.",
            }
        )

    if node.get("last_comm") is None:
        issues.append(
            {
                "severity": "unknown",
                "field": "last_comm",
                "message": "Last communication timestamp is missing.",
            }
        )

    return issues


def _highest_issue_severity(issues: list[dict[str, str]]) -> str:
    priority = {
        "critical": 4,
        "warning": 3,
        "unknown": 2,
        "info": 1,
    }
    if not issues:
        return "ok"
    return max(issues, key=lambda issue: priority.get(issue["severity"], 0))["severity"]


def _node_health_overall(severity: str) -> str:
    if severity == "critical":
        return "unhealthy"
    if severity == "warning":
        return "degraded"
    if severity == "unknown":
        return "unknown"
    return "healthy"


def _truthy_node_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "t", "yes", "y"}


def _parse_collector_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace(" ", "T"))
    except ValueError:
        return None

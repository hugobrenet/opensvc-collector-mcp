from typing import Any

import httpx

from ._formatting import compact_dict
from .instances import get_service_instances
from .inventory import get_service


async def get_service_health(svcname: str) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    try:
        service_response = await get_service(svcname)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return _unknown_service_health(svcname)
        raise

    service_rows = service_response.get("data", [])
    if not service_rows:
        return _unknown_service_health(svcname)

    service = service_rows[0]
    instances_response = await get_service_instances(svcname)
    instances = instances_response.get("data", [])
    issues = _service_health_issues(service, instances)
    severity = _worst_issue_severity(issues)
    return {
        "overall": _service_health_overall(severity),
        "severity": severity,
        "service": _service_health_service_summary(service),
        "issues": issues,
        "signals": _service_health_signals(instances),
    }


def _service_health_issues(
    service: dict[str, Any],
    instances: list[dict[str, Any]],
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    _add_status_issue(
        issues,
        field="svc_status",
        value=service.get("svc_status"),
        label="service status",
    )
    _add_status_issue(
        issues,
        field="svc_availstatus",
        value=service.get("svc_availstatus"),
        label="service availability status",
    )

    svc_frozen = _normalized_value(service.get("svc_frozen"))
    if svc_frozen and svc_frozen not in {"thawed", "false", "0", "no"}:
        issues.append(
            {
                "severity": "warning",
                "field": "svc_frozen",
                "message": f"Service frozen state is {service.get('svc_frozen')}.",
            }
        )

    placement = _normalized_value(service.get("svc_placement"))
    if placement and placement != "optimal":
        issues.append(
            {
                "severity": "warning",
                "field": "svc_placement",
                "message": f"Service placement is {service.get('svc_placement')}.",
            }
        )

    if not instances:
        issues.append(
            {
                "severity": "warning",
                "field": "instances",
                "message": "No service instance rows were returned by Collector.",
            }
        )
        return issues

    up_instances = sum(
        1
        for instance in instances
        if _normalized_value(instance.get("mon_availstatus")) == "up"
    )
    service_availstatus = _normalized_value(service.get("svc_availstatus"))
    for instance in instances:
        nodename = instance.get("nodename") or "unknown node"
        mon_availstatus = _normalized_value(instance.get("mon_availstatus"))
        if (
            mon_availstatus
            and mon_availstatus != "up"
            and not (service_availstatus == "up" and up_instances > 0)
        ):
            issues.append(
                {
                    "severity": _status_severity(mon_availstatus),
                    "field": "mon_availstatus",
                    "message": (
                        f"Instance on {nodename} has monitor availability "
                        f"{instance.get('mon_availstatus')}."
                    ),
                }
            )

        if _is_truthy(instance.get("mon_frozen")):
            issues.append(
                {
                    "severity": "warning",
                    "field": "mon_frozen",
                    "message": f"Instance on {nodename} is frozen.",
                }
            )
        if instance.get("mon_frozen_at"):
            issues.append(
                {
                    "severity": "warning",
                    "field": "mon_frozen_at",
                    "message": (
                        f"Instance on {nodename} has frozen timestamp "
                        f"{instance.get('mon_frozen_at')}."
                    ),
                }
            )
        if instance.get("mon_encap_frozen_at"):
            issues.append(
                {
                    "severity": "warning",
                    "field": "mon_encap_frozen_at",
                    "message": (
                        f"Instance on {nodename} has encap frozen timestamp "
                        f"{instance.get('mon_encap_frozen_at')}."
                    ),
                }
            )

    if up_instances == 0:
        issues.append(
            {
                "severity": "critical",
                "field": "instances",
                "message": "No service instance is reported up.",
            }
        )
    return issues


def _unknown_service_health(svcname: str) -> dict[str, Any]:
    return {
        "overall": "unknown",
        "severity": "unknown",
        "service": {"svcname": svcname},
        "issues": [
            {
                "severity": "unknown",
                "field": "svcname",
                "message": "Service was not found in Collector.",
            }
        ],
        "signals": {
            "instance_count": 0,
            "nodes": [],
            "active_nodes": [],
            "inactive_nodes": [],
            "availability_counts": {},
            "instances": [],
        },
    }


def _add_status_issue(
    issues: list[dict[str, str]],
    field: str,
    value: Any,
    label: str,
) -> None:
    status = _normalized_value(value)
    if not status or status in {"up", "ok", "thawed"}:
        return
    issues.append(
        {
            "severity": _status_severity(status),
            "field": field,
            "message": f"{label.capitalize()} is {value}.",
        }
    )


def _status_severity(status: str) -> str:
    if status in {"down", "error", "err", "failed", "failure", "critical"}:
        return "critical"
    if status in {"warn", "warning", "frozen", "n/a", "unknown"}:
        return "warning"
    return "warning"


def _worst_issue_severity(issues: list[dict[str, str]]) -> str:
    severities = {issue.get("severity") for issue in issues}
    if "critical" in severities:
        return "critical"
    if "warning" in severities:
        return "warning"
    if "unknown" in severities:
        return "unknown"
    return "ok"


def _service_health_overall(severity: str) -> str:
    return {
        "ok": "healthy",
        "warning": "degraded",
        "critical": "critical",
        "unknown": "unknown",
    }.get(severity, "unknown")


def _service_health_service_summary(service: dict[str, Any]) -> dict[str, Any]:
    return {
        "svcname": service.get("svcname"),
        "svc_status": service.get("svc_status"),
        "svc_availstatus": service.get("svc_availstatus"),
        "svc_frozen": service.get("svc_frozen"),
        "svc_topology": service.get("svc_topology"),
        "svc_nodes": service.get("svc_nodes"),
        "svc_drpnodes": service.get("svc_drpnodes"),
        "svc_placement": service.get("svc_placement"),
        "svc_ha": service.get("svc_ha"),
        "updated": service.get("updated"),
        "svc_status_updated": service.get("svc_status_updated"),
    }


def _service_health_signals(instances: list[dict[str, Any]]) -> dict[str, Any]:
    nodes = sorted(
        {
            str(instance.get("nodename"))
            for instance in instances
            if instance.get("nodename")
        }
    )
    active_nodes = sorted(
        {
            str(instance.get("nodename"))
            for instance in instances
            if instance.get("nodename")
            and _normalized_value(instance.get("mon_availstatus")) == "up"
        }
    )
    inactive_nodes = sorted(set(nodes) - set(active_nodes))
    availability_counts: dict[str, int] = {}
    for instance in instances:
        status = str(instance.get("mon_availstatus") or "unknown")
        availability_counts[status] = availability_counts.get(status, 0) + 1

    return {
        "instance_count": len(instances),
        "nodes": nodes,
        "active_nodes": active_nodes,
        "inactive_nodes": inactive_nodes,
        "availability_counts": availability_counts,
        "instances": [compact_dict(instance) for instance in instances],
    }


def _normalized_value(value: Any) -> str:
    return str(value).strip().lower() if value is not None else ""


def _is_truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return _normalized_value(value) in {"true", "1", "yes", "y", "on", "frozen"}

from typing import Any
from urllib.parse import quote

import httpx

from opensvc_collector_mcp.client import collector_get, collector_get_all


DEFAULT_LIST_SERVICE_PROPS = (
    "svcname,svc_app,svc_env,svc_status,svc_availstatus,svc_topology,"
    "svc_nodes,svc_drpnodes,svc_frozen,svc_ha,svc_created,updated"
)
SERVICE_INSTANCES_PROPS = (
    "services.svcname:svcname,services.svc_status:svc_status,"
    "services.svc_env:svc_env,services.svc_app:svc_app,"
    "services.svc_availstatus:svc_availstatus,"
    "services.svc_topology:svc_topology,nodes.nodename:nodename,"
    "svcmon.mon_vmname:mon_vmname,svcmon.mon_availstatus:mon_availstatus,"
    "svcmon.mon_frozen:mon_frozen,svcmon.mon_frozen_at:mon_frozen_at,"
    "svcmon.mon_encap_frozen_at:mon_encap_frozen_at"
)
SERVICE_RESOURCES_PROPS = (
    "nodes.nodename:nodename,rid,res_key,res_value,updated"
)


async def list_services(props: str | None = None) -> dict[str, Any]:
    selected_props = props or DEFAULT_LIST_SERVICE_PROPS
    return await collector_get_all(
        "/services",
        params={"props": selected_props},
        strategy="paged",
    )


async def search_services(
    filters: dict[str, str] | str | None = None,
    svcname: str | None = None,
    svc_app: str | None = None,
    svc_env: str | None = None,
    svc_status: str | None = None,
    svc_availstatus: str | None = None,
    svc_topology: str | None = None,
    svc_frozen: str | None = None,
    props: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    selected_props = props or DEFAULT_LIST_SERVICE_PROPS
    parsed_filters = _service_search_filters(
        filters,
        svcname=svcname,
        svc_app=svc_app,
        svc_env=svc_env,
        svc_status=svc_status,
        svc_availstatus=svc_availstatus,
        svc_topology=svc_topology,
        svc_frozen=svc_frozen,
    )
    return await collector_get(
        "/services",
        params=_service_search_params(
            filters=parsed_filters,
            props=selected_props,
            limit=limit,
            offset=offset,
        ),
    )


async def count_services(
    filters: dict[str, str] | str | None = None,
    svcname: str | None = None,
    svc_app: str | None = None,
    svc_env: str | None = None,
    svc_status: str | None = None,
    svc_availstatus: str | None = None,
    svc_topology: str | None = None,
    svc_frozen: str | None = None,
) -> dict[str, Any]:
    parsed_filters = _service_search_filters(
        filters,
        svcname=svcname,
        svc_app=svc_app,
        svc_env=svc_env,
        svc_status=svc_status,
        svc_availstatus=svc_availstatus,
        svc_topology=svc_topology,
        svc_frozen=svc_frozen,
    )
    response = await collector_get(
        "/services",
        params=_service_search_params(
            filters=parsed_filters,
            props="svcname",
            limit=1,
            offset=0,
        ),
    )
    meta = response.get("meta", {})
    return {
        "count": meta.get("total"),
        "filters": {field: value for field, value in parsed_filters},
    }


async def get_service(svcname: str) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    return await collector_get(f"/services/{quote(svcname, safe='')}")


async def get_service_instances(
    svcname: str,
    page_size: int = 1000,
    max_instances: int = 100000,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    response = await collector_get_all(
        "/services_instances",
        params=[
            ("props", SERVICE_INSTANCES_PROPS),
            ("filters", f"services.svcname={svcname}"),
        ],
        strategy="paged",
        page_size=page_size,
        max_items=max_instances,
    )
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "services_instances",
            "filter": {"services.svcname": svcname},
            "included_props": SERVICE_INSTANCES_PROPS.split(","),
        }
    )
    return {
        "svcname": svcname,
        "meta": meta,
        "data": response.get("data", []),
    }


async def get_service_resources(
    svcname: str,
    page_size: int = 1000,
    max_items: int = 200000,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    response = await collector_get_all(
        f"/services/{quote(svcname, safe='')}/resinfo",
        params={"props": SERVICE_RESOURCES_PROPS},
        strategy="paged",
        page_size=page_size,
        max_items=max_items,
    )
    rows = response.get("data", [])
    resources = _group_service_resources(rows)
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "services_resinfo",
            "filter": {"svcname": svcname},
            "included_props": SERVICE_RESOURCES_PROPS.split(","),
            "raw_count": len(rows),
            "resource_count": len(resources),
        }
    )
    return {
        "svcname": svcname,
        "meta": meta,
        "resources": resources,
    }


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


async def list_service_props() -> dict[str, Any]:
    response = await collector_get("/services", params={"props": "svcname"})
    available_props = response.get("meta", {}).get("available_props", [])
    service_props = [
        prop.removeprefix("services.")
        for prop in available_props
        if isinstance(prop, str)
    ]

    return {
        "count": len(available_props),
        "available_props": available_props,
        "service_props": service_props,
    }


def _group_service_resources(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        rid = str(row.get("rid") or "")
        nodename = str(row.get("nodename") or "")
        if not rid:
            continue

        key = (rid, nodename)
        resource = grouped.setdefault(
            key,
            {
                "rid": rid,
                "resource_type": _resource_type_from_rid(rid),
                "properties": {},
            },
        )
        if nodename:
            resource["nodename"] = nodename

        updated = row.get("updated")
        if updated and (
            not resource.get("updated") or str(updated) > str(resource["updated"])
        ):
            resource["updated"] = updated

        res_key = row.get("res_key")
        if not res_key:
            continue
        res_key = str(res_key)
        res_value = row.get("res_value")
        resource["properties"][res_key] = res_value
        if res_key in {
            "driver",
            "name",
            "monitor",
            "optional",
            "disabled",
            "shared",
            "encap",
            "standby",
            "tags",
        }:
            resource[res_key] = res_value

    return sorted(
        grouped.values(),
        key=lambda resource: (
            str(resource.get("resource_type") or ""),
            str(resource.get("rid") or ""),
            str(resource.get("nodename") or ""),
        ),
    )


def _resource_type_from_rid(rid: str) -> str:
    return rid.split("#", 1)[0] if "#" in rid else rid


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
        "instances": [_compact_dict(instance) for instance in instances],
    }


def _normalized_value(value: Any) -> str:
    return str(value).strip().lower() if value is not None else ""


def _is_truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return _normalized_value(value) in {"true", "1", "yes", "y", "on", "frozen"}


def _compact_dict(data: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in data.items() if value is not None}


def _service_search_filters(
    raw_filters: dict[str, str] | str | None = None,
    **criteria: str | None,
) -> list[tuple[str, str]]:
    filters: list[tuple[str, str]] = []
    filters.extend(_parse_service_filters(raw_filters))
    for field, value in criteria.items():
        if value is None:
            continue
        value = value.strip()
        if value:
            filters.append((field, value))
    return filters


def _parse_service_filters(raw_filters: dict[str, str] | str | None) -> list[tuple[str, str]]:
    if not raw_filters:
        return []
    if isinstance(raw_filters, dict):
        return [
            (field.strip(), value.strip())
            for field, value in raw_filters.items()
            if field.strip() and value.strip()
        ]

    filters: list[tuple[str, str]] = []
    for item in raw_filters.split(","):
        item = item.strip()
        if not item:
            continue
        if "=" not in item:
            raise ValueError("filters must use the format 'prop=value,prop=value'")
        field, value = item.split("=", 1)
        field = field.strip()
        value = value.strip()
        if not field or not value:
            raise ValueError("filters must not contain empty props or values")
        filters.append((field, value))
    return filters


def _service_search_params(
    filters: list[tuple[str, str]],
    props: str,
    limit: int,
    offset: int,
) -> list[tuple[str, Any]]:
    params: list[tuple[str, Any]] = [
        ("props", props),
        ("limit", limit),
        ("offset", offset),
    ]
    for field, value in filters:
        params.append(("filters", f"{field}={value}"))
    return params

from datetime import datetime, timedelta
from typing import Any
from urllib.parse import quote

import httpx

from opensvc_collector_mcp.client import collector_get, collector_get_all

from ._common import (
    _ensure_props_include,
    _parse_service_filters,
    get_service_identity,
)
from .inventory import (
    _service_instance_filters,
    _service_search_filters,
    get_service,
    get_service_instances,
)


SERVICE_STATUS_HISTORY_PROPS = "svc_id,svc_begin,svc_end,svc_availstatus,id"
SERVICE_INSTANCE_STATUS_HISTORY_PROPS = (
    "services.svcname:svcname,nodes.nodename:nodename,"
    "svc_id,node_id,mon_begin,mon_end,mon_availstatus,mon_overallstatus,"
    "mon_appstatus,mon_containerstatus,mon_diskstatus,mon_fsstatus,"
    "mon_hbstatus,mon_ipstatus,mon_sharestatus,mon_syncstatus,id"
)
SERVICE_ALERTS_PROPS = (
    "alert,dashboard.dash_type,dashboard.dash_severity,dashboard.dash_created,"
    "dashboard.dash_updated,dashboard.node_id,dashboard.id,"
    "dashboard.dash_env,dashboard.dash_instance"
)
SERVICE_CHECKS_PROPS = (
    "checks_live.chk_type,checks_live.chk_instance,checks_live.chk_value,"
    "checks_live.chk_err,checks_live.chk_low,checks_live.chk_high,"
    "checks_live.chk_threshold_provider,checks_live.chk_created,"
    "checks_live.chk_updated,checks_live.node_id,checks_live.id"
)
FROZEN_SERVICES_PROPS = (
    "services.svcname:svcname,services.svc_status:svc_status,"
    "services.svc_availstatus:svc_availstatus,services.svc_frozen:svc_frozen,"
    "services.svc_env:svc_env,services.svc_app:svc_app,"
    "services.svc_topology:svc_topology,nodes.nodename:nodename,"
    "svcmon.mon_vmname:mon_vmname,svcmon.mon_availstatus:mon_availstatus,"
    "svcmon.mon_frozen:mon_frozen,svcmon.mon_frozen_at:mon_frozen_at,"
    "svcmon.mon_encap_frozen_at:mon_encap_frozen_at"
)


async def get_service_checks(
    svcname: str,
    filters: dict[str, str] | str | None = None,
    chk_type: str | None = None,
    chk_err: int | str | None = None,
    node_id: str | None = None,
    chk_instance: str | None = None,
    props: str | None = None,
    page_size: int = 1000,
    max_checks: int = 10000,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    selected_props = props or SERVICE_CHECKS_PROPS
    parsed_filters = _service_check_filters(
        filters,
        chk_type=chk_type,
        chk_err=str(chk_err) if chk_err is not None else None,
        node_id=node_id,
        chk_instance=chk_instance,
    )
    response = await collector_get_all(
        f"/services/{quote(svcname, safe='')}/checks",
        params=_service_check_params(
            filters=parsed_filters,
            props=selected_props,
        ),
        strategy="paged",
        page_size=page_size,
        max_items=max_checks,
    )
    rows = response.get("data", [])
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "service_checks",
            "filter": {
                "svcname": svcname,
                **{field: value for field, value in parsed_filters},
            },
            "included_props": selected_props.split(","),
            "output_count": len(rows),
        }
    )
    return {
        "svcname": svcname,
        "meta": meta,
        "data": rows,
    }


async def get_service_alerts(
    svcname: str,
    filters: dict[str, str] | str | None = None,
    dash_type: str | None = None,
    dash_severity: int | str | None = None,
    node_id: str | None = None,
    props: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    selected_props = props or SERVICE_ALERTS_PROPS
    parsed_filters = _service_alert_filters(
        filters,
        dash_type=dash_type,
        dash_severity=str(dash_severity) if dash_severity is not None else None,
        node_id=node_id,
    )
    response = await collector_get(
        f"/services/{quote(svcname, safe='')}/alerts",
        params=_service_alert_params(
            filters=parsed_filters,
            props=selected_props,
            limit=limit,
            offset=offset,
        ),
    )
    rows = response.get("data", [])
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "service_alerts",
            "filter": {
                "svcname": svcname,
                **{field: value for field, value in parsed_filters},
            },
            "included_props": selected_props.split(","),
            "output_count": len(rows),
        }
    )
    return {
        "svcname": svcname,
        "meta": meta,
        "data": rows,
    }


async def get_service_status_history(
    svcname: str,
    filters: dict[str, str] | str | None = None,
    svc_availstatus: str | None = None,
    props: str | None = None,
    limit: int = 20,
    offset: int = 0,
    latest: bool = True,
    latest_first: bool = True,
    page_size: int = 1000,
    max_history: int = 10000,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    selected_props = props or SERVICE_STATUS_HISTORY_PROPS
    for required_prop in ("svc_id", "svc_begin", "svc_availstatus", "id"):
        selected_props = _ensure_props_include(selected_props, required_prop)
    identity = await get_service_identity(svcname)
    service = identity.get("service", {})
    svc_id = str(identity.get("svc_id") or "").strip()
    if not svc_id:
        return {
            "svcname": svcname,
            "svc_id": None,
            "service": service,
            "current_status_since": None,
            "current_history": None,
            "meta": {
                "count": 0,
                "source": "services_status_log",
                "filter": {"svcname": svcname},
                "complete": True,
                "history_count": 0,
                "output_count": 0,
            },
            "data": [],
        }

    parsed_filters = _service_status_history_filters(
        filters,
        svc_availstatus=svc_availstatus,
    )
    response = await collector_get_all(
        "/services_status_log",
        params=_service_status_history_params(
            filters=[("svc_id", svc_id), *parsed_filters],
            props=selected_props,
        ),
        strategy="paged",
        page_size=page_size,
        max_items=max_history,
    )
    rows = _sort_service_status_history_rows(
        response.get("data", []),
        latest_first=latest_first,
    )
    effective_offset = 0 if latest else offset
    output_rows = rows[effective_offset : effective_offset + limit]
    current_history = _current_service_status_history(
        rows=response.get("data", []),
        current_status=service.get("svc_availstatus"),
    )
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "services_status_log",
            "filter": {
                "svcname": svcname,
                "svc_id": svc_id,
                **{field: value for field, value in parsed_filters},
            },
            "included_props": selected_props.split(","),
            "requested_latest": latest,
            "latest_first": latest_first,
            "effective_offset": effective_offset,
            "history_count": len(rows),
            "output_count": len(output_rows),
        }
    )
    return {
        "svcname": svcname,
        "svc_id": svc_id,
        "service": service,
        "current_status_since": (
            current_history.get("svc_begin") if current_history else None
        ),
        "current_history": current_history,
        "meta": meta,
        "data": output_rows,
    }


async def get_service_instance_status_history(
    svcname: str,
    filters: dict[str, str] | str | None = None,
    node_id: str | None = None,
    nodename: str | None = None,
    mon_availstatus: str | None = None,
    mon_overallstatus: str | None = None,
    props: str | None = None,
    limit: int = 20,
    offset: int = 0,
    latest: bool = True,
    latest_first: bool = True,
    page_size: int = 1000,
    max_history: int = 1000,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    page_size = max(1, min(page_size, 5000))
    max_history = max(1, min(max_history, 100000))
    selected_props = props or SERVICE_INSTANCE_STATUS_HISTORY_PROPS
    for required_prop in (
        "svcname",
        "nodename",
        "svc_id",
        "node_id",
        "mon_begin",
        "mon_availstatus",
        "id",
    ):
        selected_props = _ensure_props_include(selected_props, required_prop)
    identity = await get_service_identity(svcname)
    service = identity.get("service", {})
    svc_id = str(identity.get("svc_id") or "").strip()
    if not svc_id:
        return {
            "svcname": svcname,
            "svc_id": None,
            "service": service,
            "meta": {
                "count": 0,
                "source": "services_instances_status_log",
                "filter": {"svcname": svcname},
                "complete": True,
                "history_count": 0,
                "output_count": 0,
            },
            "data": [],
        }

    parsed_filters = _service_instance_status_history_filters(
        filters,
        node_id=node_id,
        nodename=nodename,
        mon_availstatus=mon_availstatus,
        mon_overallstatus=mon_overallstatus,
    )
    effective_offset = 0 if latest else offset
    fetch_limit = min(max_history, limit)
    orderby = "~mon_begin" if latest or latest_first else "mon_begin"
    response = await _get_service_instance_status_history_page(
        filters=[("svc_id", svc_id), *parsed_filters],
        props=selected_props,
        orderby=orderby,
        page_size=page_size,
        max_history=fetch_limit,
        offset=effective_offset,
    )
    rows = _sort_service_instance_status_history_rows(
        response.get("data", []),
        latest_first=latest_first,
    )
    output_rows = rows[:limit]
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "services_instances_status_log",
            "filter": {
                "svcname": svcname,
                "svc_id": svc_id,
                **{field: value for field, value in parsed_filters},
            },
            "included_props": selected_props.split(","),
            "requested_latest": latest,
            "latest_first": latest_first,
            "effective_offset": effective_offset,
            "history_count": len(rows),
            "output_count": len(output_rows),
        }
    )
    return {
        "svcname": service.get("svcname") or svcname,
        "svc_id": svc_id,
        "service": service,
        "meta": meta,
        "data": output_rows,
    }


async def search_frozen_services(
    filters: dict[str, str] | str | None = None,
    min_frozen_days: int = 0,
    page_size: int = 1000,
    max_instances: int = 200000,
) -> dict[str, Any]:
    min_frozen_days = max(0, min(min_frozen_days, 3650))
    parsed_filters = _service_search_filters(filters)
    instance_filters = _service_instance_filters(parsed_filters)
    params: list[tuple[str, Any]] = [
        ("props", FROZEN_SERVICES_PROPS),
        ("filters", "svcmon.mon_frozen=1"),
    ]
    for field, value in instance_filters:
        params.append(("filters", f"{field}={value}"))

    response = await collector_get_all(
        "/services_instances",
        params=params,
        strategy="paged",
        page_size=page_size,
        max_items=max_instances,
    )
    rows = response.get("data", [])
    reference_time = datetime.now().replace(microsecond=0)
    cutoff = reference_time - timedelta(days=min_frozen_days)
    services = _group_frozen_services(
        rows=rows,
        min_frozen_days=min_frozen_days,
        cutoff=cutoff,
        reference_time=reference_time,
    )
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "services_instances",
            "filter": {
                "svcmon.mon_frozen": "1",
                **{field: value for field, value in instance_filters},
            },
            "included_props": FROZEN_SERVICES_PROPS.split(","),
            "raw_count": len(rows),
            "service_count": len(services),
            "min_frozen_days": min_frozen_days,
            "reference_time": reference_time.isoformat(sep=" "),
            "cutoff_time": cutoff.isoformat(sep=" "),
        }
    )
    return {
        "meta": meta,
        "services": services,
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


def _service_instance_status_history_filters(
    raw_filters: dict[str, str] | str | None = None,
    **criteria: str | None,
) -> list[tuple[str, str]]:
    filters = [
        (_service_instance_status_history_filter_field(field), value)
        for field, value in _parse_service_filters(raw_filters)
    ]
    for field, value in criteria.items():
        if value is None:
            continue
        value = value.strip()
        if value:
            filters.append((_service_instance_status_history_filter_field(field), value))
    return filters


def _service_instance_status_history_filter_field(field: str) -> str:
    if "." in field:
        return field
    return {
        "id": "v_svcmon_log.id",
        "svc_id": "v_svcmon_log.svc_id",
        "node_id": "v_svcmon_log.node_id",
        "nodename": "nodes.nodename",
        "mon_begin": "v_svcmon_log.mon_begin",
        "mon_end": "v_svcmon_log.mon_end",
        "mon_availstatus": "v_svcmon_log.mon_availstatus",
        "mon_overallstatus": "v_svcmon_log.mon_overallstatus",
        "mon_appstatus": "v_svcmon_log.mon_appstatus",
        "mon_containerstatus": "v_svcmon_log.mon_containerstatus",
        "mon_diskstatus": "v_svcmon_log.mon_diskstatus",
        "mon_fsstatus": "v_svcmon_log.mon_fsstatus",
        "mon_hbstatus": "v_svcmon_log.mon_hbstatus",
        "mon_ipstatus": "v_svcmon_log.mon_ipstatus",
        "mon_sharestatus": "v_svcmon_log.mon_sharestatus",
        "mon_syncstatus": "v_svcmon_log.mon_syncstatus",
    }.get(field, field)


def _service_instance_status_history_params(
    filters: list[tuple[str, str]],
    props: str,
    orderby: str,
    limit: int | None = None,
    offset: int | None = None,
) -> list[tuple[str, Any]]:
    params: list[tuple[str, Any]] = [
        ("props", props),
        ("orderby", orderby),
    ]
    if limit is not None:
        params.append(("limit", limit))
    if offset is not None:
        params.append(("offset", offset))
    for field, value in filters:
        params.append(("filters", f"{field}={value}"))
    return params


async def _get_service_instance_status_history_page(
    filters: list[tuple[str, str]],
    props: str,
    orderby: str,
    page_size: int,
    max_history: int,
    offset: int,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    scanned = 0
    total: int | None = None
    first_meta: dict[str, Any] = {}
    current_offset = offset
    while len(rows) < max_history:
        response = await collector_get(
            "/services_instances_status_log",
            params=_service_instance_status_history_params(
                filters=filters,
                props=props,
                orderby=orderby,
                limit=min(page_size, max_history - len(rows)),
                offset=current_offset,
            ),
        )
        meta = response.get("meta", {})
        data = response.get("data", [])
        if not first_meta:
            first_meta = dict(meta)
        if total is None:
            raw_total = meta.get("total")
            try:
                total = int(raw_total) if raw_total is not None else None
            except (TypeError, ValueError):
                total = None
        rows.extend(data)
        count = len(data)
        scanned += count
        current_offset += count
        if count == 0 or count < page_size:
            break
        if total is not None and current_offset >= total:
            break

    complete = total is None or current_offset >= total
    merged_meta = dict(first_meta)
    merged_meta.update(
        {
            "count": len(rows),
            "total": total if complete else None,
            "offset": offset,
            "complete": complete,
            "page_size": page_size,
            "max_items": max_history,
            "scanned": scanned,
            "strategy": "paged",
        }
    )
    return {"meta": merged_meta, "data": rows}


def _sort_service_instance_status_history_rows(
    rows: list[dict[str, Any]],
    latest_first: bool,
) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            str(row.get("mon_begin") or ""),
            str(row.get("id") or ""),
        ),
        reverse=latest_first,
    )


def _service_status_history_filters(
    raw_filters: dict[str, str] | str | None = None,
    **criteria: str | None,
) -> list[tuple[str, str]]:
    filters = [
        (_service_status_history_filter_field(field), value)
        for field, value in _parse_service_filters(raw_filters)
    ]
    for field, value in criteria.items():
        if value is None:
            continue
        value = value.strip()
        if value:
            filters.append((_service_status_history_filter_field(field), value))
    return filters


def _service_status_history_filter_field(field: str) -> str:
    if "." in field:
        return field
    return {
        "id": "v_services_log.id",
        "svc_id": "v_services_log.svc_id",
        "svc_begin": "v_services_log.svc_begin",
        "svc_end": "v_services_log.svc_end",
        "svc_availstatus": "v_services_log.svc_availstatus",
    }.get(field, field)


def _service_status_history_params(
    filters: list[tuple[str, str]],
    props: str,
) -> list[tuple[str, Any]]:
    params: list[tuple[str, Any]] = [("props", props)]
    for field, value in filters:
        params.append(("filters", f"{field}={value}"))
    return params


def _sort_service_status_history_rows(
    rows: list[dict[str, Any]],
    latest_first: bool,
) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            str(row.get("svc_begin") or ""),
            str(row.get("id") or ""),
        ),
        reverse=latest_first,
    )


def _current_service_status_history(
    rows: list[dict[str, Any]],
    current_status: Any,
) -> dict[str, Any] | None:
    current_status = str(current_status or "").strip()
    if not current_status:
        return None
    matching = [
        row
        for row in rows
        if str(row.get("svc_availstatus") or "").strip() == current_status
    ]
    if not matching:
        return None
    return _sort_service_status_history_rows(matching, latest_first=True)[0]


def _service_check_filters(
    raw_filters: dict[str, str] | str | None = None,
    **criteria: str | None,
) -> list[tuple[str, str]]:
    filters = [
        (_service_check_filter_field(field), value)
        for field, value in _parse_service_filters(raw_filters)
    ]
    for field, value in criteria.items():
        if value is None:
            continue
        value = value.strip()
        if value:
            filters.append((_service_check_filter_field(field), value))
    return filters


def _service_check_filter_field(field: str) -> str:
    if "." in field:
        return field
    return {
        "id": "checks_live.id",
        "svc_id": "checks_live.svc_id",
        "node_id": "checks_live.node_id",
        "chk_type": "checks_live.chk_type",
        "chk_instance": "checks_live.chk_instance",
        "chk_value": "checks_live.chk_value",
        "chk_err": "checks_live.chk_err",
        "chk_low": "checks_live.chk_low",
        "chk_high": "checks_live.chk_high",
        "chk_threshold_provider": "checks_live.chk_threshold_provider",
        "chk_created": "checks_live.chk_created",
        "chk_updated": "checks_live.chk_updated",
    }.get(field, field)


def _service_check_params(
    filters: list[tuple[str, str]],
    props: str,
) -> list[tuple[str, Any]]:
    params: list[tuple[str, Any]] = [("props", props)]
    for field, value in filters:
        params.append(("filters", f"{field}={value}"))
    return params


def _service_alert_filters(
    raw_filters: dict[str, str] | str | None = None,
    **criteria: str | None,
) -> list[tuple[str, str]]:
    filters = [
        (_service_alert_filter_field(field), value)
        for field, value in _parse_service_filters(raw_filters)
    ]
    for field, value in criteria.items():
        if value is None:
            continue
        value = value.strip()
        if value:
            filters.append((_service_alert_filter_field(field), value))
    return filters


def _service_alert_filter_field(field: str) -> str:
    if "." in field:
        return field
    return {
        "id": "dashboard.id",
        "dash_type": "dashboard.dash_type",
        "dash_severity": "dashboard.dash_severity",
        "dash_created": "dashboard.dash_created",
        "dash_updated": "dashboard.dash_updated",
        "dash_env": "dashboard.dash_env",
        "dash_instance": "dashboard.dash_instance",
        "node_id": "dashboard.node_id",
        "svc_id": "dashboard.svc_id",
    }.get(field, field)


def _service_alert_params(
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


def _group_frozen_services(
    rows: list[dict[str, Any]],
    min_frozen_days: int,
    cutoff: datetime,
    reference_time: datetime,
) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for row in rows:
        svcname = row.get("svcname")
        if not svcname:
            continue
        svcname = str(svcname)
        service = grouped.setdefault(
            svcname,
            {
                "svcname": svcname,
                "svc_env": row.get("svc_env"),
                "svc_app": row.get("svc_app"),
                "svc_status": row.get("svc_status"),
                "svc_availstatus": row.get("svc_availstatus"),
                "svc_frozen": row.get("svc_frozen"),
                "svc_topology": row.get("svc_topology"),
                "nodes": [],
                "instances": [],
            },
        )
        for field in (
            "svc_env",
            "svc_app",
            "svc_status",
            "svc_availstatus",
            "svc_frozen",
            "svc_topology",
        ):
            if service.get(field) is None and row.get(field) is not None:
                service[field] = row.get(field)

        nodename = row.get("nodename")
        if nodename and nodename not in service["nodes"]:
            service["nodes"].append(nodename)

        frozen_at = _first_datetime(
            row.get("mon_frozen_at"),
            row.get("mon_encap_frozen_at"),
        )
        service["instances"].append(
            _compact_dict(
                {
                    "nodename": row.get("nodename"),
                    "mon_vmname": row.get("mon_vmname"),
                    "mon_availstatus": row.get("mon_availstatus"),
                    "mon_frozen": row.get("mon_frozen"),
                    "mon_frozen_at": row.get("mon_frozen_at"),
                    "mon_encap_frozen_at": row.get("mon_encap_frozen_at"),
                }
            )
        )
        if frozen_at and (
            not service.get("_frozen_since_dt")
            or frozen_at < service["_frozen_since_dt"]
        ):
            service["_frozen_since_dt"] = frozen_at

    services: list[dict[str, Any]] = []
    for service in grouped.values():
        frozen_since = service.pop("_frozen_since_dt", None)
        if min_frozen_days and (not frozen_since or frozen_since > cutoff):
            continue
        service["nodes"] = sorted(str(node) for node in service["nodes"])
        service["frozen_instance_count"] = len(service["instances"])
        if frozen_since:
            service["frozen_since"] = frozen_since.isoformat(sep=" ")
            service["frozen_days"] = max(0, (reference_time - frozen_since).days)
        services.append(service)

    return sorted(
        services,
        key=lambda service: (
            service.get("frozen_since") or "",
            service.get("svcname") or "",
        ),
    )


def _first_datetime(*values: Any) -> datetime | None:
    dates = [_parse_collector_datetime(value) for value in values]
    dates = [date for date in dates if date is not None]
    return min(dates) if dates else None


def _parse_collector_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


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

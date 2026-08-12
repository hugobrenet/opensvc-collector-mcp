from typing import Any

from opensvc_collector_mcp.client import collector_get_page

from ._common import (
    _ensure_props_include,
    _parse_service_filters,
    get_service_identity,
)


SERVICE_STATUS_HISTORY_PROPS = "svc_id,svc_begin,svc_end,svc_availstatus,id"


async def get_service_status_history(
    svcname: str,
    filters: dict[str, str] | str | None = None,
    svc_availstatus: str | None = None,
    props: str | None = None,
    orderby: str | None = "~svc_begin",
    limit: int = 20,
    offset: int = 0,
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
            "pagination": {
                "limit": limit,
                "offset": offset,
                "returned": 0,
                "next_offset": None,
                "complete": True,
                "truncated": False,
            },
            "data": [],
        }

    parsed_filters = _service_status_history_filters(
        filters,
        svc_availstatus=svc_availstatus,
    )
    response = await collector_get_page(
        "/services_status_log",
        params=_service_status_history_params(
            filters=[("svc_id", svc_id), *parsed_filters],
            props=selected_props,
            orderby=orderby,
            limit=limit,
            offset=offset,
        ),
    )
    rows = response.get("data", [])
    current_history = await _get_current_service_status_history(
        svc_id=svc_id,
        current_status=service.get("svc_availstatus"),
        props=selected_props,
    )
    return {
        "svcname": svcname,
        "svc_id": svc_id,
        "service": service,
        "current_status_since": (
            current_history.get("svc_begin") if current_history else None
        ),
        "current_history": current_history,
        "pagination": response["pagination"],
        "data": rows,
    }


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
    orderby: str | None,
    limit: int,
    offset: int,
) -> list[tuple[str, Any]]:
    params: list[tuple[str, Any]] = [
        ("props", props),
        ("limit", limit),
        ("offset", offset),
    ]
    if orderby:
        params.append(("orderby", orderby))
    for field, value in filters:
        params.append(("filters", f"{field}={value}"))
    return params


async def _get_current_service_status_history(
    svc_id: str,
    current_status: Any,
    props: str,
) -> dict[str, Any] | None:
    current_status = str(current_status or "").strip()
    if not current_status:
        return None
    response = await collector_get_page(
        "/services_status_log",
        params=_service_status_history_params(
            filters=[
                ("svc_id", svc_id),
                ("v_services_log.svc_availstatus", current_status),
            ],
            props=props,
            orderby="~svc_begin",
            limit=1,
            offset=0,
        ),
    )
    rows = response.get("data", [])
    return rows[0] if rows else None

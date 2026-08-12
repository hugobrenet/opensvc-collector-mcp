from typing import Any

from opensvc_collector_mcp.client import collector_get_page

from ._common import (
    _ensure_props_include,
    _parse_service_filters,
    get_service_identity,
)


SERVICE_INSTANCE_STATUS_HISTORY_PROPS = (
    "services.svcname:svcname,nodes.nodename:nodename,"
    "svc_id,node_id,mon_begin,mon_end,mon_availstatus,mon_overallstatus,"
    "mon_appstatus,mon_containerstatus,mon_diskstatus,mon_fsstatus,"
    "mon_hbstatus,mon_ipstatus,mon_sharestatus,mon_syncstatus,id"
)


async def get_service_instance_status_history(
    svcname: str,
    filters: dict[str, str] | str | None = None,
    node_id: str | None = None,
    nodename: str | None = None,
    mon_availstatus: str | None = None,
    mon_overallstatus: str | None = None,
    props: str | None = None,
    orderby: str | None = "~mon_begin",
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    limit = max(1, min(limit, 100))
    offset = max(0, offset)
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

    parsed_filters = _service_instance_status_history_filters(
        filters,
        node_id=node_id,
        nodename=nodename,
        mon_availstatus=mon_availstatus,
        mon_overallstatus=mon_overallstatus,
    )
    response = await collector_get_page(
        "/services_instances_status_log",
        params=_service_instance_status_history_params(
            filters=[("svc_id", svc_id), *parsed_filters],
            props=selected_props,
            orderby=orderby,
            limit=limit,
            offset=offset,
        ),
    )
    return {
        "svcname": service.get("svcname") or svcname,
        "svc_id": svc_id,
        "service": service,
        "pagination": response["pagination"],
        "data": response.get("data", []),
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
            filters.append(
                (_service_instance_status_history_filter_field(field), value)
            )
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
    orderby: str | None,
    limit: int | None = None,
    offset: int | None = None,
) -> list[tuple[str, Any]]:
    params: list[tuple[str, Any]] = [("props", props)]
    if orderby:
        params.append(("orderby", orderby))
    if limit is not None:
        params.append(("limit", limit))
    if offset is not None:
        params.append(("offset", offset))
    for field, value in filters:
        params.append(("filters", f"{field}={value}"))
    return params

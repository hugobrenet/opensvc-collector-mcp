from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get_page
from opensvc_collector_mcp.core.collection import collection_params

from ._common import _parse_service_filters


SERVICE_ALERTS_PROPS = (
    "alert,dashboard.dash_type,dashboard.dash_severity,dashboard.dash_created,"
    "dashboard.dash_updated,dashboard.node_id,dashboard.id,"
    "dashboard.dash_env,dashboard.dash_instance"
)


async def get_service_alerts(
    svcname: str,
    filters: dict[str, str] | str | None = None,
    dash_type: str | None = None,
    dash_severity: int | str | None = None,
    node_id: str | None = None,
    props: str | None = None,
    orderby: str | None = "~dashboard.dash_updated",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    limit = max(1, min(limit, 1000))
    offset = max(0, offset)
    selected_props = props or SERVICE_ALERTS_PROPS
    parsed_filters = _service_alert_filters(
        filters,
        dash_type=dash_type,
        dash_severity=str(dash_severity) if dash_severity is not None else None,
        node_id=node_id,
    )
    response = await collector_get_page(
        f"/services/{quote(svcname, safe='')}/alerts",
        params=collection_params(
            filters=parsed_filters,
            props=selected_props,
            orderby=orderby,
            search=search,
            limit=limit,
            offset=offset,
        ),
    )
    return {"svcname": svcname, **response}


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

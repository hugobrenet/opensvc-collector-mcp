from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get_page
from opensvc_collector_mcp.core.collection import collection_params

from ._common import _parse_service_filters


SERVICE_CHECKS_PROPS = (
    "checks_live.chk_type,checks_live.chk_instance,checks_live.chk_value,"
    "checks_live.chk_err,checks_live.chk_low,checks_live.chk_high,"
    "checks_live.chk_threshold_provider,checks_live.chk_created,"
    "checks_live.chk_updated,checks_live.node_id,checks_live.id"
)


async def get_service_checks(
    svcname: str,
    filters: dict[str, str] | str | None = None,
    chk_type: str | None = None,
    chk_err: int | str | None = None,
    node_id: str | None = None,
    chk_instance: str | None = None,
    props: str | None = None,
    orderby: str | None = "checks_live.chk_type",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
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
    response = await collector_get_page(
        f"/services/{quote(svcname, safe='')}/checks",
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

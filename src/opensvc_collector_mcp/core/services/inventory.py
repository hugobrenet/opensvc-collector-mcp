from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get, collector_get_page
from opensvc_collector_mcp.core.utils import collection_params

from ._common import _parse_service_filters


DEFAULT_LIST_SERVICE_PROPS = (
    "svcname,svc_app,svc_env,svc_status,svc_availstatus,svc_topology,"
    "svc_nodes,svc_drpnodes,svc_frozen,svc_ha,svc_created,updated"
)


async def list_services(
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "svcname",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    limit = max(1, min(limit, 1000))
    offset = max(0, offset)
    selected_props = props or DEFAULT_LIST_SERVICE_PROPS
    parsed_filters = _service_search_filters(filters)
    return await collector_get_page(
        "/services",
        params=_service_search_params(
            filters=parsed_filters,
            props=selected_props,
            orderby=orderby,
            search=search,
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
            orderby=None,
            search=None,
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


def _service_search_params(
    filters: list[tuple[str, str]],
    props: str,
    orderby: str | None,
    search: str | None,
    limit: int,
    offset: int,
) -> list[tuple[str, Any]]:
    return collection_params(
        filters=filters,
        props=props,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )

from typing import Any
from urllib.parse import quote

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

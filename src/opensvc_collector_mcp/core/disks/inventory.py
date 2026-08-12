from typing import Any
from urllib.parse import quote

import httpx

from opensvc_collector_mcp.client import collector_get, collector_get_page
from opensvc_collector_mcp.core.collection import collection_params, parse_collector_filters


DISK_FILTER_ALIASES = {
    "node_id": "svcdisks.node_id",
    "svc_id": "svcdisks.svc_id",
    "app_id": "svcdisks.app_id",
    "disk_id": "diskinfo.disk_id",
    "disk_local": "svcdisks.disk_local",
    "disk_group": "diskinfo.disk_group",
    "disk_arrayid": "diskinfo.disk_arrayid",
    "array_name": "stor_array.array_name",
}


DEFAULT_LIST_DISK_PROPS = (
    "svcdisks.id:id,svcdisks.node_id:node_id,svcdisks.svc_id:svc_id,"
    "svcdisks.app_id:app_id,svcdisks.disk_id:disk_id,"
    "svcdisks.disk_size:disk_size,svcdisks.disk_used:disk_used,"
    "svcdisks.disk_local:disk_local,svcdisks.disk_dg:disk_dg,"
    "svcdisks.disk_vendor:disk_vendor,svcdisks.disk_model:disk_model,"
    "svcdisks.disk_region:disk_region,svcdisks.disk_updated:disk_updated,"
    "diskinfo.id:diskinfo_id,diskinfo.disk_id:diskinfo_disk_id,"
    "diskinfo.disk_name:disk_name,diskinfo.disk_devid:disk_devid,"
    "diskinfo.disk_alloc:disk_alloc,diskinfo.disk_level:disk_level,"
    "diskinfo.disk_raid:disk_raid,diskinfo.disk_group:disk_group,"
    "diskinfo.disk_arrayid:disk_arrayid,"
    "diskinfo.disk_controller:disk_controller,"
    "diskinfo.disk_created:disk_created,"
    "diskinfo.disk_updated:diskinfo_updated,"
    "stor_array.id:array_id,stor_array.array_name:array_name,"
    "stor_array.array_model:array_model,"
    "stor_array.array_firmware:array_firmware"
)


def _normalize_disk_filters(filters: list[tuple[str, str]]) -> list[tuple[str, str]]:
    return [(DISK_FILTER_ALIASES.get(field, field), value) for field, value in filters]


def _strip_disk_prefix(prop: str) -> str:
    for prefix in ("svcdisks.", "diskinfo.", "stor_array."):
        if prop.startswith(prefix):
            return prop.removeprefix(prefix)
    return prop


async def list_disks(
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    selected_props = props or DEFAULT_LIST_DISK_PROPS
    parsed_filters = _normalize_disk_filters(parse_collector_filters(filters))
    return await collector_get_page(
        "/disks",
        params=collection_params(
            filters=parsed_filters,
            props=selected_props,
            orderby=orderby,
            search=search,
            limit=limit,
            offset=offset,
        ),
    )


async def count_disks(
    filters: dict[str, str] | str | None = None,
    search: str | None = None,
) -> dict[str, Any]:
    parsed_filters = _normalize_disk_filters(parse_collector_filters(filters))
    response = await collector_get(
        "/disks",
        params=collection_params(
            filters=parsed_filters,
            props=None,
            orderby=None,
            search=search,
            limit=1,
            offset=0,
        ),
    )
    meta = response.get("meta", {})
    return {
        "count": meta.get("total", len(response.get("data", []))),
        "filters": {field: value for field, value in parsed_filters},
        "search": search,
    }


async def get_disk(
    disk: str,
    props: str | None = None,
) -> dict[str, Any]:
    selector = disk.strip()
    if not selector:
        raise ValueError("disk must not be empty")

    selected_props = props or DEFAULT_LIST_DISK_PROPS
    try:
        response = await collector_get(
            f"/disks/{quote(selector, safe='')}",
            params={"props": selected_props},
        )
        source = "disk_detail"
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code != 404:
            raise
        response = await collector_get(
            "/disks",
            params=collection_params(
                filters=[("diskinfo.disk_id", selector)],
                props=selected_props,
                limit=1000,
                offset=0,
            ),
        )
        source = "disk_detail_by_filter"

    rows = response.get("data", [])
    meta = dict(response.get("meta", {}) or {})
    meta.update(
        {
            "source": source,
            "selector": selector,
            "count": len(rows) if isinstance(rows, list) else 0,
        }
    )
    return {"disk": selector, "meta": meta, "data": rows if isinstance(rows, list) else []}


async def list_disk_props() -> dict[str, Any]:
    response = await collector_get(
        "/disks",
        params={"limit": 1, "offset": 0},
    )
    available_props = response.get("meta", {}).get("available_props", [])
    disk_props = [
        _strip_disk_prefix(prop)
        for prop in available_props
        if isinstance(prop, str)
    ]

    return {
        "count": len(available_props),
        "available_props": available_props,
        "disk_props": disk_props,
    }

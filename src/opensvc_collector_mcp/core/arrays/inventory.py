from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get, collector_get_all
from opensvc_collector_mcp.core.utils import collection_params, parse_collector_filters


DEFAULT_LIST_ARRAY_PROPS = (
    "id,array_name,array_model,array_firmware,array_cache,"
    "array_level,array_comment,array_updated"
)
DEFAULT_ARRAY_DISKGROUP_PROPS = (
    "id,array_id,dg_name,dg_size,dg_free,dg_used,dg_reserved,dg_updated"
)
DEFAULT_ARRAY_PROXY_PROPS = "id,array_id,node_id"
DEFAULT_ARRAY_TARGET_PROPS = "id,array_id,array_tgtid"


async def list_arrays(
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "array_name",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    selected_props = props or DEFAULT_LIST_ARRAY_PROPS
    parsed_filters = parse_collector_filters(filters)
    return await collector_get(
        "/arrays",
        params=collection_params(
            filters=parsed_filters,
            props=selected_props,
            orderby=orderby,
            search=search,
            limit=limit,
            offset=offset,
        ),
    )


async def count_array_diskgroups(
    array: str,
) -> dict[str, Any]:
    selector = array.strip()
    if not selector:
        raise ValueError("array must not be empty")

    response = await collector_get(
        f"/arrays/{quote(selector, safe='')}/diskgroups",
        params={"props": "dg_name", "limit": 1, "offset": 0},
    )
    meta = response.get("meta", {})
    return {
        "array": selector,
        "count": meta.get("total", len(response.get("data", []))),
        "meta": {
            "source": "arrays/<id>/diskgroups",
            "selector": selector,
            "raw_meta": meta,
        },
    }


async def count_arrays(
    filters: dict[str, str] | str | None = None,
    search: str | None = None,
) -> dict[str, Any]:
    parsed_filters = parse_collector_filters(filters)
    response = await collector_get(
        "/arrays",
        params=collection_params(
            filters=parsed_filters,
            props="array_name",
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


async def get_array(
    array: str,
    props: str | None = None,
) -> dict[str, Any]:
    selector = array.strip()
    if not selector:
        raise ValueError("array must not be empty")

    params = {"props": props} if props else None
    response = await collector_get(
        f"/arrays/{quote(selector, safe='')}",
        params=params,
    )
    rows = response.get("data", [])
    meta = dict(response.get("meta") or {})
    meta.update(
        {
            "source": "array_detail",
            "selector": selector,
            "count": len(rows) if isinstance(rows, list) else 0,
        }
    )
    return {"meta": meta, "data": rows if isinstance(rows, list) else []}


async def get_array_diskgroup(
    array: str,
    diskgroup: str,
    props: str | None = None,
) -> dict[str, Any]:
    selector = array.strip()
    diskgroup_selector = diskgroup.strip()
    if not selector:
        raise ValueError("array must not be empty")
    if not diskgroup_selector:
        raise ValueError("diskgroup must not be empty")

    params = {"props": props} if props else None
    response = await collector_get(
        (
            f"/arrays/{quote(selector, safe='')}/diskgroups/"
            f"{quote(diskgroup_selector, safe='')}"
        ),
        params=params,
    )
    rows = response.get("data", [])
    meta = dict(response.get("meta") or {})
    meta.update(
        {
            "source": "arrays/<id>/diskgroups/<id>",
            "selector": selector,
            "diskgroup_selector": diskgroup_selector,
            "count": len(rows) if isinstance(rows, list) else 0,
        }
    )
    return {
        "array": selector,
        "diskgroup": diskgroup_selector,
        "meta": meta,
        "data": rows if isinstance(rows, list) else [],
    }


async def get_array_diskgroups(
    array: str,
    props: str | None = None,
    max_diskgroups: int = 200000,
) -> dict[str, Any]:
    selector = array.strip()
    if not selector:
        raise ValueError("array must not be empty")

    selected_props = props or DEFAULT_ARRAY_DISKGROUP_PROPS
    response = await collector_get_all(
        f"/arrays/{quote(selector, safe='')}/diskgroups",
        params={"props": selected_props},
        max_items=max_diskgroups,
    )
    rows = response.get("data", [])
    meta = dict(response.get("meta") or {})
    meta.update(
        {
            "source": "arrays/<id>/diskgroups",
            "selector": selector,
            "included_props": selected_props.split(","),
            "diskgroup_count": len(rows),
        }
    )
    return {
        "array": selector,
        "meta": meta,
        "data": rows,
    }


async def get_array_proxies(
    array: str,
    props: str | None = None,
    max_proxies: int = 200000,
) -> dict[str, Any]:
    selector = array.strip()
    if not selector:
        raise ValueError("array must not be empty")

    selected_props = props or DEFAULT_ARRAY_PROXY_PROPS
    response = await collector_get_all(
        f"/arrays/{quote(selector, safe='')}/proxies",
        params={"props": selected_props},
        max_items=max_proxies,
    )
    rows = response.get("data", [])
    meta = dict(response.get("meta") or {})
    meta.update(
        {
            "source": "arrays/<id>/proxies",
            "selector": selector,
            "included_props": selected_props.split(","),
            "proxy_count": len(rows),
        }
    )
    return {
        "array": selector,
        "meta": meta,
        "data": rows,
    }


async def get_array_targets(
    array: str,
    props: str | None = None,
    max_targets: int = 200000,
) -> dict[str, Any]:
    selector = array.strip()
    if not selector:
        raise ValueError("array must not be empty")

    selected_props = props or DEFAULT_ARRAY_TARGET_PROPS
    response = await collector_get_all(
        f"/arrays/{quote(selector, safe='')}/targets",
        params={"props": selected_props},
        max_items=max_targets,
    )
    rows = response.get("data", [])
    meta = dict(response.get("meta") or {})
    meta.update(
        {
            "source": "arrays/<id>/targets",
            "selector": selector,
            "included_props": selected_props.split(","),
            "target_count": len(rows),
        }
    )
    return {
        "array": selector,
        "meta": meta,
        "data": rows,
    }


async def list_array_props() -> dict[str, Any]:
    response = await collector_get("/arrays", params={"props": "array_name", "limit": 1})
    available_props = response.get("meta", {}).get("available_props", [])
    array_props = [
        prop.removeprefix("stor_array.")
        for prop in available_props
        if isinstance(prop, str)
    ]

    return {
        "count": len(available_props),
        "available_props": available_props,
        "array_props": array_props,
    }

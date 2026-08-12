from typing import Any

from opensvc_collector_mcp.client import collector_get, collector_get_page
from opensvc_collector_mcp.core.utils import collection_params, parse_collector_filters

from ._common import quote_selector, require_selector


DEFAULT_ARRAY_DISKGROUP_PROPS = (
    "id,array_id,dg_name,dg_size,dg_free,dg_used,dg_reserved,dg_updated"
)


async def list_array_diskgroups(
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "dg_name",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    selected_props = props or DEFAULT_ARRAY_DISKGROUP_PROPS
    parsed_filters = parse_collector_filters(filters)
    return await collector_get_page(
        "/arrays_diskgroups",
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
    selector = require_selector(array, "array")
    response = await collector_get(
        f"/arrays/{quote_selector(selector)}/diskgroups",
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


async def get_array_diskgroup(
    array: str,
    diskgroup: str,
    props: str | None = None,
) -> dict[str, Any]:
    selector = require_selector(array, "array")
    diskgroup_selector = require_selector(diskgroup, "diskgroup")
    params = {"props": props} if props else None
    response = await collector_get(
        (
            f"/arrays/{quote_selector(selector)}/diskgroups/"
            f"{quote_selector(diskgroup_selector)}"
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
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "dg_name",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    selector = require_selector(array, "array")
    selected_props = props or DEFAULT_ARRAY_DISKGROUP_PROPS
    response = await collector_get_page(
        f"/arrays/{quote_selector(selector)}/diskgroups",
        params=collection_params(
            filters=parse_collector_filters(filters),
            props=selected_props,
            orderby=orderby,
            search=search,
            limit=limit,
            offset=offset,
        ),
    )
    return {"array": selector, **response}

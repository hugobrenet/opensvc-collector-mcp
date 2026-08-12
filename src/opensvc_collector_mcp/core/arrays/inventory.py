from typing import Any

from opensvc_collector_mcp.client import collector_get, collector_get_page
from opensvc_collector_mcp.core.collection import collection_params, parse_collector_filters

from ._common import quote_selector, require_selector


DEFAULT_LIST_ARRAY_PROPS = (
    "id,array_name,array_model,array_firmware,array_cache,"
    "array_level,array_comment,array_updated"
)


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
    return await collector_get_page(
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
    selector = require_selector(array, "array")
    params = {"props": props} if props else None
    response = await collector_get(
        f"/arrays/{quote_selector(selector)}",
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


async def list_array_props() -> dict[str, Any]:
    response = await collector_get(
        "/arrays",
        params={"props": "array_name", "limit": 1},
    )
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

from typing import Any

from opensvc_collector_mcp.client import collector_get
from opensvc_collector_mcp.core.utils import collection_params, parse_collector_filters


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

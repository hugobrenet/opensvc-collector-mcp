from typing import Any

from opensvc_collector_mcp.client import collector_get
from opensvc_collector_mcp.core.utils import collection_params, parse_collector_filters


DEFAULT_LIST_TAG_PROPS = "tag_id,tag_name,tag_exclude,tag_created"


async def list_tags(
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "tag_name",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    selected_props = props or DEFAULT_LIST_TAG_PROPS
    parsed_filters = parse_collector_filters(filters)
    return await collector_get(
        "/tags",
        params=collection_params(
            filters=parsed_filters,
            props=selected_props,
            orderby=orderby,
            search=search,
            limit=limit,
            offset=offset,
        ),
    )


async def list_tag_props() -> dict[str, Any]:
    response = await collector_get("/tags", params={"props": "tag_id", "limit": 1})
    available_props = response.get("meta", {}).get("available_props", [])
    tag_props = [
        prop.removeprefix("tags.")
        for prop in available_props
        if isinstance(prop, str)
    ]

    return {
        "count": len(available_props),
        "available_props": available_props,
        "tag_props": tag_props,
    }

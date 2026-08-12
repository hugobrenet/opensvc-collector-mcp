from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get, collector_get_page
from opensvc_collector_mcp.core.collection import collection_params, parse_collector_filters

from ._read import resolve_tag_selector


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
    return await collector_get_page(
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


async def count_tags(
    filters: dict[str, str] | str | None = None,
) -> dict[str, Any]:
    parsed_filters = parse_collector_filters(filters)
    response = await collector_get(
        "/tags",
        params=collection_params(
            filters=parsed_filters,
            props="tag_id",
            orderby=None,
            search=None,
            limit=1,
            offset=0,
        ),
    )
    meta = response.get("meta", {})
    return {
        "count": meta.get("total", len(response.get("data", []))),
        "filters": {field: value for field, value in parsed_filters},
    }


async def get_tag(
    tag_id: str | None = None,
    tag_name: str | None = None,
    props: str | None = None,
) -> dict[str, Any]:
    resolved = await resolve_tag_selector(tag_id=tag_id, tag_name=tag_name)
    params = {"props": props} if props else None
    response = await collector_get(
        f"/tags/{quote(resolved['tag_id'], safe='')}",
        params=params,
    )
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "tag_detail",
            "selector": resolved["selector"],
            "resolution": resolved["resolution"],
            "resolved_tag_id": resolved["tag_id"],
            "resolved_tag_name": resolved.get("tag_name"),
            "count": len(response.get("data", [])),
        }
    )
    return {"meta": meta, "data": response.get("data", [])}


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

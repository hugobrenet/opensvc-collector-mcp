from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get, collector_get_all
from opensvc_collector_mcp.core.utils import collection_params, parse_collector_filters


DEFAULT_LIST_TAG_PROPS = "tag_id,tag_name,tag_exclude,tag_created"
DEFAULT_TAG_NODE_PROPS = (
    "nodename,status,asset_env,node_env,loc_city,loc_country,"
    "app,team_responsible,os_name"
)


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


async def get_tag(
    tag_id: str | None = None,
    tag_name: str | None = None,
    props: str | None = None,
) -> dict[str, Any]:
    resolved = await _resolve_tag_selector(tag_id=tag_id, tag_name=tag_name)
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


async def get_tag_nodes(
    tag_id: str | None = None,
    tag_name: str | None = None,
    props: str | None = None,
    max_nodes: int = 200000,
) -> dict[str, Any]:
    resolved = await _resolve_tag_selector(tag_id=tag_id, tag_name=tag_name)
    selected_props = props or DEFAULT_TAG_NODE_PROPS
    response = await collector_get_all(
        f"/tags/{quote(resolved['tag_id'], safe='')}/nodes",
        params={"props": selected_props},
        max_items=max_nodes,
    )
    rows = response.get("data", [])
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "tags/<tag_id>/nodes",
            "selector": resolved["selector"],
            "resolution": resolved["resolution"],
            "filter": {
                "tag_id": resolved["tag_id"],
                "tag_name": resolved.get("tag_name"),
            },
            "included_props": selected_props.split(","),
            "node_count": len(rows),
        }
    )
    return {
        "tag_id": resolved["tag_id"],
        "tag_name": resolved.get("tag_name"),
        "tag": resolved.get("tag"),
        "meta": meta,
        "data": rows,
    }


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


async def _resolve_tag_selector(
    tag_id: str | None = None,
    tag_name: str | None = None,
) -> dict[str, Any]:
    cleaned_tag_id = tag_id.strip() if tag_id else None
    cleaned_tag_name = tag_name.strip() if tag_name else None
    if bool(cleaned_tag_id) == bool(cleaned_tag_name):
        raise ValueError("provide exactly one of tag_id or tag_name")

    if cleaned_tag_id:
        return {
            "selector": cleaned_tag_id,
            "resolution": "tag_id",
            "tag_id": cleaned_tag_id,
        }

    response = await collector_get(
        "/tags",
        params=collection_params(
            filters=[("tag_name", cleaned_tag_name or "")],
            props="tag_id,tag_name",
            orderby=None,
            search=None,
            limit=2,
            offset=0,
        ),
    )
    rows = response.get("data", [])
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"tag_name {cleaned_tag_name!r} not found")

    exact_rows = [row for row in rows if str(row.get("tag_name") or "") == cleaned_tag_name]
    if len(exact_rows) != 1:
        raise ValueError(f"tag_name {cleaned_tag_name!r} matched {len(exact_rows)} tags")

    row = exact_rows[0]
    resolved_tag_id = str(row.get("tag_id") or "").strip()
    if not resolved_tag_id:
        raise ValueError(f"tag_name {cleaned_tag_name!r} resolved without tag_id")
    return {
        "selector": cleaned_tag_name,
        "resolution": "tag_name",
        "tag_id": resolved_tag_id,
        "tag_name": row.get("tag_name"),
        "tag": row,
    }

from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get, collector_get_all
from opensvc_collector_mcp.core.utils import collection_params, parse_collector_filters


async def get_node_tags(
    nodename: str,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "tag_name",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    nodename = nodename.strip()
    if not nodename:
        raise ValueError("nodename must not be empty")

    parsed_filters = parse_collector_filters(filters)
    response = await collector_get(
        f"/nodes/{quote(nodename, safe='')}/tags",
        params=collection_params(
            filters=parsed_filters,
            props=props,
            orderby=orderby,
            search=search,
            limit=limit,
            offset=offset,
        ),
    )
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "node_tags",
            "filter": {"nodename": nodename, **{field: value for field, value in parsed_filters}},
            "included_props": props.split(",") if props else meta.get("included_props", []),
            "output_count": len(response.get("data", [])),
        }
    )
    return {"nodename": nodename, "meta": meta, "data": response.get("data", [])}


async def search_node_by_tag(tag_name: str) -> dict[str, Any]:
    tag_name = tag_name.strip()
    if not tag_name:
        raise ValueError("tag_name must not be empty")

    tag_response = await collector_get(
        "/tags",
        params=[
            ("filters", f"tag_name={tag_name}"),
            ("limit", 1),
            ("offset", 0),
        ],
    )
    tag_rows = tag_response.get("data", [])
    if not tag_rows:
        return {
            "tag_name": tag_name,
            "tag_id": None,
            "meta": {"count": 0, "source": "tags"},
            "data": [],
        }

    tag = tag_rows[0]
    tag_id = tag.get("tag_id")
    if not tag_id:
        return {
            "tag_name": tag_name,
            "tag_id": None,
            "meta": {"count": 0, "source": "tags"},
            "data": [],
        }

    response = await collector_get_all(
        f"/tags/{quote(str(tag_id), safe='')}/nodes",
    )
    data = response.get("data", [])
    return {
        "tag_name": tag_name,
        "tag_id": str(tag_id),
        "meta": response.get("meta", {}),
        "data": data,
    }


async def search_nodes_without_tag(tag_name: str) -> dict[str, Any]:
    tag_name = tag_name.strip()
    if not tag_name:
        raise ValueError("tag_name must not be empty")

    tagged = await search_node_by_tag(tag_name)
    tagged_names = {
        str(row.get("nodename")).strip()
        for row in tagged.get("data", [])
        if str(row.get("nodename", "")).strip()
    }

    all_nodes = await collector_get_all(
        "/nodes",
        params={"props": "nodename"},
    )
    all_rows = all_nodes.get("data", [])
    data = [
        row
        for row in all_rows
        if str(row.get("nodename", "")).strip() not in tagged_names
    ]
    meta = all_nodes.get("meta", {})
    return {
        "tag_name": tag_name,
        "tag_id": tagged.get("tag_id"),
        "meta": {
            "count": len(data),
            "tagged_count": len(tagged_names),
            "total_nodes": meta.get("total", len(all_rows)),
            "source": "nodes - tags/<tag_id>/nodes",
        },
        "data": data,
    }

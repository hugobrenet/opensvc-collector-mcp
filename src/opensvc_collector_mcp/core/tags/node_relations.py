from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import (
    collector_delete,
    collector_get,
    collector_get_page,
    collector_post,
)
from opensvc_collector_mcp.core.nodes._common import resolve_node_reference
from opensvc_collector_mcp.core.prechecks import clean_value, require_single_row
from opensvc_collector_mcp.core.utils import collection_params, parse_collector_filters

from ._common import resolve_tag_reference
from ._read import resolve_tag_selector


DEFAULT_TAG_NODE_PROPS = (
    "nodename,status,asset_env,node_env,loc_city,loc_country,"
    "app,team_responsible,os_name"
)
DEFAULT_TAG_NODE_WRITE_PROPS = (
    "node_id,nodename,status,updated,node_env,asset_env,"
    "team_responsible,loc_city"
)


async def attach_tag_to_node(
    *,
    tag_id: str | None = None,
    tag_name: str | None = None,
    node_id: str | None = None,
    nodename: str | None = None,
    tag_attach_data: str | None = None,
) -> dict[str, Any]:
    selector_tag_id = clean_value(tag_id)
    selector_tag_name = clean_value(tag_name)
    selector_node_id = clean_value(node_id)
    selector_nodename = clean_value(nodename)

    tag = await resolve_tag_reference(
        tag_id=selector_tag_id or None,
        tag_name=selector_tag_name or None,
        operation="attach tag to node",
        missing_message="attach tag to node requires tag_id or tag_name",
    )
    node = await resolve_node_reference(
        node_id=selector_node_id or None,
        nodename=selector_nodename or None,
        props=DEFAULT_TAG_NODE_WRITE_PROPS,
        operation="attach tag to node",
        missing_message="attach tag to node requires node_id or nodename",
    )

    resolved_tag_id = clean_value(tag.get("tag_id"))
    resolved_tag_name = clean_value(tag.get("tag_name"))
    resolved_node_id = clean_value(node.get("node_id"))
    resolved_nodename = clean_value(node.get("nodename"))
    payload = None
    if tag_attach_data is not None:
        payload = {"tag_attach_data": tag_attach_data}

    path = (
        f"/tags/{quote(resolved_tag_id, safe='')}/nodes/"
        f"{quote(resolved_node_id, safe='')}"
    )
    response = await collector_post(path, data=payload)
    return {
        "tag_id": resolved_tag_id,
        "tag_name": resolved_tag_name,
        "tag": tag,
        "node_id": resolved_node_id,
        "nodename": resolved_nodename,
        "node": node,
        "attached": True,
        "tag_attach_data": tag_attach_data,
        "collector_response": response,
        "meta": {
            "source": "tags/<tag_id>/nodes/<node_id>",
            "tag_selector": (
                "tag_id+tag_name"
                if selector_tag_id and selector_tag_name
                else "tag_id" if selector_tag_id else "tag_name"
            ),
            "node_selector": (
                "node_id+nodename"
                if selector_node_id and selector_nodename
                else "node_id" if selector_node_id else "nodename"
            ),
        },
    }


async def detach_tag_from_node(
    *,
    tag_id: str | None = None,
    tag_name: str | None = None,
    node_id: str | None = None,
    nodename: str | None = None,
) -> dict[str, Any]:
    selector_tag_id = clean_value(tag_id)
    selector_tag_name = clean_value(tag_name)
    selector_node_id = clean_value(node_id)
    selector_nodename = clean_value(nodename)

    tag = await resolve_tag_reference(
        tag_id=selector_tag_id or None,
        tag_name=selector_tag_name or None,
        operation="detach tag from node",
        missing_message="detach tag from node requires tag_id or tag_name",
    )
    node = await resolve_node_reference(
        node_id=selector_node_id or None,
        nodename=selector_nodename or None,
        props=DEFAULT_TAG_NODE_WRITE_PROPS,
        operation="detach tag from node",
        missing_message="detach tag from node requires node_id or nodename",
    )

    resolved_tag_id = clean_value(tag.get("tag_id"))
    resolved_tag_name = clean_value(tag.get("tag_name"))
    resolved_node_id = clean_value(node.get("node_id"))
    resolved_nodename = clean_value(node.get("nodename"))
    relation = await _ensure_tag_node_relation_exists(
        tag_id=resolved_tag_id,
        node_id=resolved_node_id,
    )

    path = (
        f"/tags/{quote(resolved_tag_id, safe='')}/nodes/"
        f"{quote(resolved_node_id, safe='')}"
    )
    response = await collector_delete(path)
    return {
        "tag_id": resolved_tag_id,
        "tag_name": resolved_tag_name,
        "tag": tag,
        "node_id": resolved_node_id,
        "nodename": resolved_nodename,
        "node": node,
        "relation": relation,
        "detached": True,
        "collector_response": response,
        "meta": {
            "source": "tags/<tag_id>/nodes/<node_id>",
            "tag_selector": (
                "tag_id+tag_name"
                if selector_tag_id and selector_tag_name
                else "tag_id" if selector_tag_id else "tag_name"
            ),
            "node_selector": (
                "node_id+nodename"
                if selector_node_id and selector_nodename
                else "node_id" if selector_node_id else "nodename"
            ),
            "precheck": "tag_node_relation_exists",
        },
    }


async def count_tag_nodes(
    tag_id: str | None = None,
    tag_name: str | None = None,
) -> dict[str, Any]:
    resolved = await resolve_tag_selector(tag_id=tag_id, tag_name=tag_name)
    response = await collector_get(
        f"/tags/{quote(resolved['tag_id'], safe='')}/nodes",
        params={"props": "nodename", "limit": 1, "offset": 0},
    )
    meta = response.get("meta", {})
    return {
        "tag_id": resolved["tag_id"],
        "tag_name": resolved.get("tag_name"),
        "tag": resolved.get("tag"),
        "count": meta.get("total", len(response.get("data", []))),
        "meta": {
            "source": "tags/<tag_id>/nodes",
            "selector": resolved["selector"],
            "resolution": resolved["resolution"],
            "raw_meta": meta,
        },
    }


async def get_tag_nodes(
    tag_id: str | None = None,
    tag_name: str | None = None,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "nodename",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    resolved = await resolve_tag_selector(tag_id=tag_id, tag_name=tag_name)
    selected_props = props or DEFAULT_TAG_NODE_PROPS
    response = await collector_get_page(
        f"/tags/{quote(resolved['tag_id'], safe='')}/nodes",
        params=collection_params(
            filters=parse_collector_filters(filters),
            props=selected_props,
            orderby=orderby,
            search=search,
            limit=limit,
            offset=offset,
        ),
    )
    return {
        "tag_id": resolved["tag_id"],
        "tag_name": resolved.get("tag_name"),
        "tag": resolved.get("tag"),
        **response,
    }


async def _ensure_tag_node_relation_exists(
    *,
    tag_id: str,
    node_id: str,
) -> dict[str, Any]:
    response = await collector_get(
        f"/tags/{quote(tag_id, safe='')}/nodes",
        params=collection_params(
            filters=[("node_id", node_id)],
            props="node_id,nodename",
            orderby=None,
            search=None,
            limit=2,
            offset=0,
        ),
    )
    return require_single_row(
        response,
        not_found_message=(
            "detach tag from node relation not found: "
            f"tag_id={tag_id} node_id={node_id}"
        ),
        multiple_message=(
            "detach tag from node relation is ambiguous or missing node_id: "
            f"tag_id={tag_id} node_id={node_id}"
        ),
        invalid_message="detach tag from node resolved relation payload is invalid",
        exact_match_field="node_id",
        exact_match_value=node_id,
    )

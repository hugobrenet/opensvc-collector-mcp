from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import (
    collector_delete,
    collector_get,
    collector_get_all,
    collector_post,
)
from opensvc_collector_mcp.core.utils import collection_params, parse_collector_filters
from opensvc_collector_mcp.core.nodes._common import resolve_node_reference
from opensvc_collector_mcp.core.services._common import resolve_service_reference
from opensvc_collector_mcp.core.prechecks import clean_value, require_single_row
from opensvc_collector_mcp.core.tags._common import (
    resolve_single_tag_selector,
    resolve_tag_reference,
)


DEFAULT_LIST_TAG_PROPS = "tag_id,tag_name,tag_exclude,tag_created"
DEFAULT_TAG_NODE_PROPS = (
    "nodename,status,asset_env,node_env,loc_city,loc_country,"
    "app,team_responsible,os_name"
)
DEFAULT_TAG_SERVICE_PROPS = (
    "svcname,svc_app,svc_env,svc_status,svc_availstatus,svc_topology,"
    "svc_nodes,svc_drpnodes,svc_frozen,svc_ha,svc_created,updated"
)
DEFAULT_TAG_NODE_WRITE_PROPS = (
    "node_id,nodename,status,updated,node_env,asset_env,"
    "team_responsible,loc_city"
)
DEFAULT_TAG_SERVICE_WRITE_PROPS = (
    "svc_id,svcname,svc_app,svc_env,svc_status,"
    "svc_availstatus,svc_topology,updated"
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


async def create_tag(
    tag_name: str,
    tag_data: str | None = None,
    tag_exclude: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"tag_name": tag_name.strip()}
    if not payload["tag_name"]:
        raise ValueError("tag_name must not be empty")
    if tag_data is not None:
        payload["tag_data"] = tag_data
    if tag_exclude is not None:
        payload["tag_exclude"] = tag_exclude

    return await collector_post("/tags", data=payload)


async def delete_tag(
    *,
    tag_id: str | None = None,
    tag_name: str | None = None,
    confirm_tag_id: str,
    confirm_tag_name: str,
) -> dict[str, Any]:
    selector_tag_id = tag_id.strip() if tag_id else ""
    selector_tag_name = tag_name.strip() if tag_name else ""
    confirmation_id = confirm_tag_id.strip() if confirm_tag_id else ""
    confirmation_name = confirm_tag_name.strip() if confirm_tag_name else ""

    if not confirmation_id:
        raise ValueError("confirm_tag_id must not be empty")
    if not confirmation_name:
        raise ValueError("confirm_tag_name must not be empty")
    if selector_tag_id and confirmation_id != selector_tag_id:
        raise ValueError("confirm_tag_id must match tag_id")

    tag = await resolve_single_tag_selector(
        tag_id=selector_tag_id or None,
        tag_name=selector_tag_name or None,
        operation="delete tag",
    )
    resolved_tag_id = str(tag.get("tag_id") or "").strip()
    resolved_tag_name = str(tag.get("tag_name") or "").strip()
    if confirmation_id != resolved_tag_id:
        raise ValueError("confirm_tag_id must match the resolved tag_id")
    if confirmation_name != resolved_tag_name:
        raise ValueError("confirm_tag_name must match the resolved tag_name")

    response = await collector_delete(f"/tags/{quote(resolved_tag_id, safe='')}")
    return {
        "tag_id": resolved_tag_id,
        "tag_name": resolved_tag_name,
        "tag": tag,
        "deleted": True,
        "collector_response": response,
        "meta": {
            "source": "tags/<tag_id>",
            "selector": "tag_id" if selector_tag_id else "tag_name",
            "confirmation": ["confirm_tag_id", "confirm_tag_name"],
        },
    }


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


async def attach_tag_to_service(
    *,
    tag_id: str | None = None,
    tag_name: str | None = None,
    svc_id: str | None = None,
    svcname: str | None = None,
) -> dict[str, Any]:
    selector_tag_id = clean_value(tag_id)
    selector_tag_name = clean_value(tag_name)
    selector_svc_id = clean_value(svc_id)
    selector_svcname = clean_value(svcname)

    tag = await resolve_tag_reference(
        tag_id=selector_tag_id or None,
        tag_name=selector_tag_name or None,
        operation="attach tag to service",
        missing_message="attach tag to service requires tag_id or tag_name",
    )
    service = await resolve_service_reference(
        svc_id=selector_svc_id or None,
        svcname=selector_svcname or None,
        props=DEFAULT_TAG_SERVICE_WRITE_PROPS,
        operation="attach tag to service",
        missing_message="attach tag to service requires svc_id or svcname",
    )

    resolved_tag_id = clean_value(tag.get("tag_id"))
    resolved_tag_name = clean_value(tag.get("tag_name"))
    resolved_svc_id = clean_value(service.get("svc_id"))
    resolved_svcname = clean_value(service.get("svcname"))

    path = (
        f"/tags/{quote(resolved_tag_id, safe='')}/services/"
        f"{quote(resolved_svc_id, safe='')}"
    )
    response = await collector_post(path)
    return {
        "tag_id": resolved_tag_id,
        "tag_name": resolved_tag_name,
        "tag": tag,
        "svc_id": resolved_svc_id,
        "svcname": resolved_svcname,
        "service": service,
        "attached": True,
        "collector_response": response,
        "meta": {
            "source": "tags/<tag_id>/services/<svc_id>",
            "tag_selector": (
                "tag_id+tag_name"
                if selector_tag_id and selector_tag_name
                else "tag_id" if selector_tag_id else "tag_name"
            ),
            "service_selector": (
                "svc_id+svcname"
                if selector_svc_id and selector_svcname
                else "svc_id" if selector_svc_id else "svcname"
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


async def count_tag_nodes(
    tag_id: str | None = None,
    tag_name: str | None = None,
) -> dict[str, Any]:
    resolved = await _resolve_tag_selector(tag_id=tag_id, tag_name=tag_name)
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


async def count_tag_services(
    tag_id: str | None = None,
    tag_name: str | None = None,
    max_services: int = 200000,
) -> dict[str, Any]:
    resolved = await _resolve_tag_selector(tag_id=tag_id, tag_name=tag_name)
    response = await collector_get_all(
        f"/tags/{quote(resolved['tag_id'], safe='')}/services",
        params={"props": "svcname"},
        max_items=max_services,
    )
    raw_rows = response.get("data", [])
    rows = _dedupe_rows_by_key(raw_rows, "svcname")
    meta = dict(response.get("meta", {}))
    return {
        "tag_id": resolved["tag_id"],
        "tag_name": resolved.get("tag_name"),
        "tag": resolved.get("tag"),
        "count": len(rows),
        "raw_count": len(raw_rows),
        "duplicate_count": len(raw_rows) - len(rows),
        "meta": {
            **meta,
            "source": "tags/<tag_id>/services",
            "selector": resolved["selector"],
            "resolution": resolved["resolution"],
            "complete": meta.get("complete"),
            "max_services": max_services,
        },
    }


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


async def get_tag_services(
    tag_id: str | None = None,
    tag_name: str | None = None,
    props: str | None = None,
    max_services: int = 200000,
) -> dict[str, Any]:
    resolved = await _resolve_tag_selector(tag_id=tag_id, tag_name=tag_name)
    selected_props = _ensure_props_include(props or DEFAULT_TAG_SERVICE_PROPS, "svcname")
    response = await collector_get_all(
        f"/tags/{quote(resolved['tag_id'], safe='')}/services",
        params={"props": selected_props},
        max_items=max_services,
    )
    raw_rows = response.get("data", [])
    rows = _dedupe_rows_by_key(raw_rows, "svcname")
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "tags/<tag_id>/services",
            "selector": resolved["selector"],
            "resolution": resolved["resolution"],
            "filter": {
                "tag_id": resolved["tag_id"],
                "tag_name": resolved.get("tag_name"),
            },
            "included_props": selected_props.split(","),
            "raw_count": len(raw_rows),
            "service_count": len(rows),
            "duplicate_count": len(raw_rows) - len(rows),
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


def _ensure_props_include(props: str, required: str) -> str:
    selected = [prop.strip() for prop in props.split(",") if prop.strip()]
    if required not in selected:
        selected.insert(0, required)
    return ",".join(selected)


def _dedupe_rows_by_key(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        value = str(row.get(key, "")).strip()
        if not value or value in seen:
            continue
        seen.add(value)
        deduped.append(row)
    return deduped

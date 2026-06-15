from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_delete, collector_get, collector_post
from opensvc_collector_mcp.core.utils import collection_params
from opensvc_collector_mcp.core.nodes._common import _ensure_node_nodename_available


DEFAULT_SEARCH_NODE_PROPS = (
    "nodename,status,asset_env,node_env,loc_city,loc_country,"
    "app,team_responsible,os_name"
)
DEFAULT_NODE_DELETE_SNAPSHOT_PROPS = (
    "node_id,nodename,status,asset_env,node_env,app,team_responsible,updated"
)

NODE_UPDATE_ALLOWED_PROPERTIES = frozenset(
    {
        "action_type",
        "app",
        "asset_env",
        "assetname",
        "cluster_id",
        "collector",
        "connect_to",
        "enclosure",
        "enclosureslot",
        "fqdn",
        "hv",
        "hvpool",
        "hvvdc",
        "hw_obs_alert_date",
        "hw_obs_warn_date",
        "last_comm",
        "listener_port",
        "loc_addr",
        "loc_building",
        "loc_city",
        "loc_country",
        "loc_floor",
        "loc_rack",
        "loc_room",
        "loc_zip",
        "maintenance_end",
        "manufacturer",
        "node_frozen",
        "node_frozen_at",
        "node_id",
        "nodename",
        "notifications",
        "os_obs_alert_date",
        "os_obs_warn_date",
        "power_breaker1",
        "power_breaker2",
        "power_cabinet1",
        "power_cabinet2",
        "power_protect",
        "power_protect_breaker",
        "power_supply_nb",
        "role",
        "sec_zone",
        "snooze_till",
        "status",
        "team_integ",
        "team_responsible",
        "team_support",
        "type",
        "tz",
        "updated",
        "version",
        "warranty_end",
    }
)


async def list_nodes(
    filters: dict[str, str] | str | None = None,
    nodename_contains: str | None = None,
    props: str | None = None,
    orderby: str | None = "nodename",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
    max_scan: int = 5000,
) -> dict[str, Any]:
    limit = max(1, min(limit, 1000))
    offset = max(0, offset)
    selected_props = props or DEFAULT_SEARCH_NODE_PROPS
    parsed_filters = _node_search_filters(filters)

    if not nodename_contains:
        return await collector_get(
            "/nodes",
            params=_node_search_params(
                filters=parsed_filters,
                props=selected_props,
                orderby=orderby,
                search=search,
                limit=limit,
                offset=offset,
            ),
        )

    max_scan = max(limit + offset, min(max_scan, 50000))
    selected_props = _props_with_required(selected_props, "nodename")

    needle = nodename_contains.strip().lower()
    if not needle:
        raise ValueError("nodename_contains must not be empty")

    matches: list[dict[str, Any]] = []
    scanned = 0
    api_offset = 0
    page_size = min(max(limit + offset, 100), 1000)
    total_candidates: int | None = None

    while scanned < max_scan:
        response = await collector_get(
            "/nodes",
            params=_node_search_params(
                filters=parsed_filters,
                props=selected_props,
                orderby=orderby,
                search=search,
                limit=min(page_size, max_scan - scanned),
                offset=api_offset,
            ),
        )
        meta = response.get("meta", {})
        data = response.get("data", [])
        if total_candidates is None:
            total_candidates = meta.get("total")

        for node in data:
            nodename = str(node.get("nodename", "")).lower()
            if needle in nodename:
                matches.append(node)

        count = len(data)
        scanned += count
        api_offset += count
        if count == 0 or count < page_size or len(matches) >= offset + limit:
            break

    result_data = matches[offset : offset + limit]
    complete = total_candidates is None or api_offset >= total_candidates
    return {
        "meta": {
            "count": len(result_data),
            "total": len(matches) if complete else None,
            "limit": limit,
            "offset": offset,
            "scanned": scanned,
            "max_scan": max_scan,
            "complete": complete,
            "filters": {
                "nodename_contains": nodename_contains,
                **{field: value for field, value in parsed_filters},
            },
            "included_props": selected_props.split(","),
        },
        "data": result_data,
    }


async def list_node_props() -> dict[str, Any]:
    response = await collector_get("/nodes", params={"props": "nodename"})
    available_props = response.get("meta", {}).get("available_props", [])
    node_props = [
        prop.removeprefix("nodes.") for prop in available_props if isinstance(prop, str)
    ]

    return {
        "count": len(available_props),
        "available_props": available_props,
        "node_props": node_props,
    }


async def count_nodes(
    filters: dict[str, str] | str | None = None,
    status: str | None = None,
    asset_env: str | None = None,
    node_env: str | None = None,
    loc_city: str | None = None,
    loc_country: str | None = None,
    team_responsible: str | None = None,
    app: str | None = None,
    os_name: str | None = None,
) -> dict[str, Any]:
    parsed_filters = _node_search_filters(
        filters,
        status=status,
        asset_env=asset_env,
        node_env=node_env,
        loc_city=loc_city,
        loc_country=loc_country,
        team_responsible=team_responsible,
        app=app,
        os_name=os_name,
    )
    response = await collector_get(
        "/nodes",
        params=_node_search_params(
            filters=parsed_filters,
            props="nodename",
            orderby=None,
            search=None,
            limit=1,
            offset=0,
        ),
    )
    meta = response.get("meta", {})
    return {
        "count": meta.get("total"),
        "filters": {field: value for field, value in parsed_filters},
    }


async def get_node(nodename: str) -> dict[str, Any]:
    nodename = nodename.strip()
    if not nodename:
        raise ValueError("nodename must not be empty")

    return await collector_get(f"/nodes/{quote(nodename, safe='')}")


async def create_node(
    nodename: str,
    properties: dict[str, Any] | None = None,
) -> dict[str, Any]:
    nodename = nodename.strip()
    if not nodename:
        raise ValueError("nodename must not be empty")

    await _ensure_node_nodename_available(nodename)
    payload = _normalized_node_create_payload(nodename, properties)
    response = await collector_post("/nodes", data=payload)
    return {
        "nodename": nodename,
        "submitted_properties": payload,
        "collector_response": response,
        "meta": {
            "source": "nodes",
            "precheck": "nodename_absent",
            "collector_validates_payload": True,
        },
    }


async def update_node_properties(
    nodename: str,
    properties: dict[str, Any],
) -> dict[str, Any]:
    nodename = nodename.strip()
    if not nodename:
        raise ValueError("nodename must not be empty")

    payload = _normalized_node_write_payload(properties)
    response = await collector_post(f"/nodes/{quote(nodename, safe='')}", data=payload)
    return {
        "nodename": nodename,
        "updated_properties": payload,
        "collector_response": response,
        "meta": {
            "source": "nodes/<nodename>",
            "allowed_properties": sorted(NODE_UPDATE_ALLOWED_PROPERTIES),
        },
    }


async def delete_node(
    node_id: str,
    confirm_node_id: str,
    confirm_nodename: str,
) -> dict[str, Any]:
    node_id = node_id.strip()
    confirmation_id = confirm_node_id.strip() if confirm_node_id else ""
    confirmation_name = confirm_nodename.strip() if confirm_nodename else ""

    if not node_id:
        raise ValueError("node_id must not be empty")
    if confirmation_id != node_id:
        raise ValueError("confirm_node_id must match node_id")
    if not confirmation_name:
        raise ValueError("confirm_nodename must not be empty")

    node = await _get_node_delete_snapshot(node_id)
    resolved_node_id = str(node.get("node_id") or "").strip()
    resolved_nodename = str(node.get("nodename") or "").strip()
    if not resolved_node_id:
        raise ValueError("resolved node has no node_id; refusing to delete")
    if resolved_node_id != node_id:
        raise ValueError(
            "node_id must be the exact Collector node_id, not a nodename; "
            "resolve the node first with list_nodes using "
            "props=node_id,nodename,app"
        )
    if not resolved_nodename:
        raise ValueError("resolved node has no nodename; refusing to delete")
    if confirmation_name != resolved_nodename:
        raise ValueError("confirm_nodename must match the resolved nodename")

    response = await collector_delete(f"/nodes/{quote(node_id, safe='')}")
    return {
        "node_id": node_id,
        "nodename": resolved_nodename,
        "node": node,
        "deleted": True,
        "collector_response": response,
        "meta": {
            "source": "nodes/<node_id>",
            "selector": "node_id",
            "confirmation": ["confirm_node_id", "confirm_nodename"],
        },
    }


async def _get_node_delete_snapshot(node_id: str) -> dict[str, Any]:
    response = await collector_get(
        f"/nodes/{quote(node_id, safe='')}",
        params={"props": DEFAULT_NODE_DELETE_SNAPSHOT_PROPS},
    )
    data = response.get("data", [])
    if not data:
        raise ValueError("node_id not found")
    if len(data) != 1:
        raise ValueError("node_id resolved to multiple nodes; refusing to delete")
    node = data[0]
    if not isinstance(node, dict):
        raise ValueError("resolved node payload is invalid; refusing to delete")
    return node


def _normalized_node_create_payload(
    nodename: str,
    properties: dict[str, Any] | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for raw_key, value in (properties or {}).items():
        key = raw_key.strip()
        if key:
            payload[key] = value
    payload["nodename"] = nodename
    return payload


def _normalized_node_write_payload(properties: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for raw_key, value in properties.items():
        key = raw_key.strip()
        if not key:
            raise ValueError("node property names must not be empty")
        payload[key] = value

    if not payload:
        raise ValueError("properties must not be empty")

    forbidden = sorted(set(payload) - NODE_UPDATE_ALLOWED_PROPERTIES)
    if forbidden:
        allowed = ", ".join(sorted(NODE_UPDATE_ALLOWED_PROPERTIES))
        rejected = ", ".join(forbidden)
        raise ValueError(f"unsupported node writable properties: {rejected}; allowed: {allowed}")

    return payload


def _props_with_required(props: str, *required_props: str) -> str:
    selected = [prop.strip() for prop in props.split(",") if prop.strip()]
    for prop in required_props:
        if prop not in selected:
            selected.append(prop)
    return ",".join(selected)


def _node_search_filters(
    raw_filters: dict[str, str] | str | None = None,
    **criteria: str | None,
) -> list[tuple[str, str]]:
    filters: list[tuple[str, str]] = []
    filters.extend(_parse_node_filters(raw_filters))
    for field, value in criteria.items():
        if value is None:
            continue
        value = value.strip()
        if value:
            filters.append((field, value))
    return filters


def _parse_node_filters(
    raw_filters: dict[str, str] | str | None,
) -> list[tuple[str, str]]:
    if not raw_filters:
        return []
    if isinstance(raw_filters, dict):
        return [
            (field.strip(), value.strip())
            for field, value in raw_filters.items()
            if field.strip() and value.strip()
        ]

    filters: list[tuple[str, str]] = []
    for item in raw_filters.split(","):
        item = item.strip()
        if not item:
            continue
        if "=" not in item:
            raise ValueError("filters must use the format 'prop=value,prop=value'")
        field, value = item.split("=", 1)
        field = field.strip()
        value = value.strip()
        if not field or not value:
            raise ValueError("filters must not contain empty props or values")
        filters.append((field, value))
    return filters


def _node_search_params(
    filters: list[tuple[str, str]],
    props: str,
    orderby: str | None,
    search: str | None,
    limit: int,
    offset: int,
) -> list[tuple[str, Any]]:
    return collection_params(
        filters=filters,
        props=props,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )

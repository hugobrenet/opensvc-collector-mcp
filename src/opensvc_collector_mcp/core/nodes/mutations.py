from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_delete, collector_post

from ._common import _ensure_node_nodename_available, resolve_single_node_selector


DEFAULT_NODE_DELETE_SNAPSHOT_PROPS = (
    "node_id,nodename,status,asset_env,node_env,app,team_responsible,updated"
)
DEFAULT_NODE_UPDATE_SNAPSHOT_PROPS = (
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
    nodename: str | None = None,
    properties: dict[str, Any] | None = None,
    *,
    node_id: str | None = None,
) -> dict[str, Any]:
    selector_node_id = node_id.strip() if node_id else ""
    selector_nodename = nodename.strip() if nodename else ""

    node = await resolve_single_node_selector(
        node_id=selector_node_id or None,
        nodename=selector_nodename or None,
        props=DEFAULT_NODE_UPDATE_SNAPSHOT_PROPS,
        operation="update node properties",
    )
    resolved_node_id = str(node.get("node_id") or "").strip()
    resolved_nodename = str(node.get("nodename") or "").strip()

    payload = _normalized_node_write_payload(properties or {})
    response = await collector_post(
        f"/nodes/{quote(resolved_nodename, safe='')}",
        data=payload,
    )
    return {
        "nodename": resolved_nodename,
        "updated_properties": payload,
        "collector_response": response,
        "meta": {
            "source": "nodes/<nodename>",
            "selector": "node_id" if selector_node_id else "nodename",
            "resolved_node_id": resolved_node_id,
            "node": node,
            "allowed_properties": sorted(NODE_UPDATE_ALLOWED_PROPERTIES),
        },
    }


async def delete_node(
    *,
    node_id: str | None = None,
    nodename: str | None = None,
) -> dict[str, Any]:
    selector_node_id = node_id.strip() if node_id else ""
    selector_nodename = nodename.strip() if nodename else ""

    node = await resolve_single_node_selector(
        node_id=selector_node_id or None,
        nodename=selector_nodename or None,
        props=DEFAULT_NODE_DELETE_SNAPSHOT_PROPS,
        operation="delete node",
    )
    resolved_node_id = str(node.get("node_id") or "").strip()
    resolved_nodename = str(node.get("nodename") or "").strip()

    response = await collector_delete(f"/nodes/{quote(resolved_node_id, safe='')}")
    return {
        "node_id": resolved_node_id,
        "nodename": resolved_nodename,
        "node": node,
        "deleted": True,
        "collector_response": response,
        "meta": {
            "source": "nodes/<node_id>",
            "selector": "node_id" if selector_node_id else "nodename",
        },
    }


def _normalized_node_create_payload(
    nodename: str,
    properties: dict[str, Any] | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for raw_key, value in (properties or {}).items():
        key = raw_key.strip()
        if key:
            payload[key] = value
    forbidden = sorted(set(payload) & {"node_id", "nodename"})
    if forbidden:
        rejected = ", ".join(forbidden)
        raise ValueError(
            f"create_node properties must not include reserved fields: {rejected}"
        )
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
        raise ValueError(
            f"unsupported node writable properties: {rejected}; allowed: {allowed}"
        )

    return payload

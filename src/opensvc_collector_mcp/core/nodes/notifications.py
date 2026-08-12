from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_post

from ._common import resolve_single_node_selector


DEFAULT_NODE_SNOOZE_SNAPSHOT_PROPS = "node_id,nodename,status,snooze_till,updated"


async def snooze_node_notifications(
    *,
    node_id: str | None = None,
    nodename: str | None = None,
    duration: str,
) -> dict[str, Any]:
    selector_node_id = node_id.strip() if node_id else ""
    selector_nodename = nodename.strip() if nodename else ""
    duration = duration.strip() if duration else ""
    if not duration:
        raise ValueError("duration must not be empty")

    node = await resolve_single_node_selector(
        node_id=selector_node_id or None,
        nodename=selector_nodename or None,
        props=DEFAULT_NODE_SNOOZE_SNAPSHOT_PROPS,
        operation="snooze node notifications",
    )
    resolved_node_id = str(node.get("node_id") or "").strip()
    resolved_nodename = str(node.get("nodename") or "").strip()

    response = await collector_post(
        f"/nodes/{quote(resolved_node_id, safe='')}/snooze",
        data={"duration": duration},
    )
    return {
        "node_id": resolved_node_id,
        "nodename": resolved_nodename,
        "duration": duration,
        "node": node,
        "snoozed": True,
        "collector_response": response,
        "meta": {
            "source": "nodes/<node_id>/snooze",
            "selector": "node_id" if selector_node_id else "nodename",
        },
    }


async def unsnooze_node_notifications(
    *,
    node_id: str | None = None,
    nodename: str | None = None,
) -> dict[str, Any]:
    selector_node_id = node_id.strip() if node_id else ""
    selector_nodename = nodename.strip() if nodename else ""

    node = await resolve_single_node_selector(
        node_id=selector_node_id or None,
        nodename=selector_nodename or None,
        props=DEFAULT_NODE_SNOOZE_SNAPSHOT_PROPS,
        operation="unsnooze node notifications",
    )
    resolved_node_id = str(node.get("node_id") or "").strip()
    resolved_nodename = str(node.get("nodename") or "").strip()

    response = await collector_post(f"/nodes/{quote(resolved_node_id, safe='')}/snooze")
    return {
        "node_id": resolved_node_id,
        "nodename": resolved_nodename,
        "node": node,
        "unsnoozed": True,
        "collector_response": response,
        "meta": {
            "source": "nodes/<node_id>/snooze",
            "selector": "node_id" if selector_node_id else "nodename",
        },
    }

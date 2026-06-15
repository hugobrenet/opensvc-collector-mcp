from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get
from opensvc_collector_mcp.core.utils import collection_params


def _first_node_row(response: dict[str, Any], nodename: str) -> dict[str, Any]:
    data = response.get("data", [])
    if data:
        return data[0]
    return {"nodename": nodename.strip()}


def _empty_to_none(value: Any) -> Any:
    if value == "":
        return None
    return value


DEFAULT_NODE_SELECTOR_PROPS = "node_id,nodename,status,snooze_till,updated"


async def resolve_single_node_selector(
    *,
    node_id: str | None = None,
    nodename: str | None = None,
    props: str = DEFAULT_NODE_SELECTOR_PROPS,
    operation: str = "node operation",
) -> dict[str, Any]:
    node_id = node_id.strip() if node_id else ""
    nodename = nodename.strip() if nodename else ""
    if bool(node_id) == bool(nodename):
        raise ValueError(
            f"{operation} requires exactly one node selector: node_id or nodename"
        )

    if node_id:
        node = await _resolve_node_id_selector(
            node_id=node_id,
            props=props,
            operation=operation,
        )
    else:
        node = await _resolve_nodename_selector(
            nodename=nodename,
            props=props,
            operation=operation,
        )

    resolved_node_id = str(node.get("node_id") or "").strip()
    resolved_nodename = str(node.get("nodename") or "").strip()
    if not resolved_node_id:
        raise ValueError(f"{operation} resolved node has no node_id")
    if not resolved_nodename:
        raise ValueError(f"{operation} resolved node has no nodename")
    return node


async def _resolve_node_id_selector(
    *,
    node_id: str,
    props: str,
    operation: str,
) -> dict[str, Any]:
    response = await collector_get(
        f"/nodes/{quote(node_id, safe='')}",
        params={"props": props},
    )
    data = response.get("data", [])
    if not data:
        raise ValueError(f"{operation} node_id not found: {node_id}")
    if len(data) != 1:
        raise ValueError(f"{operation} node_id resolved to multiple nodes: {node_id}")
    node = data[0]
    if not isinstance(node, dict):
        raise ValueError(f"{operation} resolved node payload is invalid")

    resolved_node_id = str(node.get("node_id") or "").strip()
    if resolved_node_id != node_id:
        raise ValueError(
            f"{operation} node_id selector did not resolve to the exact node_id; "
            "retry with a node_id from list_nodes"
        )
    return node


async def _resolve_nodename_selector(
    *,
    nodename: str,
    props: str,
    operation: str,
) -> dict[str, Any]:
    response = await collector_get(
        "/nodes",
        params=collection_params(
            filters=[("nodename", nodename)],
            props=props,
            orderby=None,
            search=None,
            limit=2,
            offset=0,
        ),
    )
    data = response.get("data", [])
    if not data:
        raise ValueError(f"{operation} nodename not found: {nodename}")
    if len(data) != 1:
        raise ValueError(
            f"{operation} nodename is ambiguous: {nodename}; "
            "retry with node_id from list_nodes"
        )
    node = data[0]
    if not isinstance(node, dict):
        raise ValueError(f"{operation} resolved node payload is invalid")
    return node


async def _ensure_node_nodename_available(nodename: str) -> None:
    response = await collector_get(
        "/nodes",
        params=collection_params(
            filters=[("nodename", nodename)],
            props="node_id,nodename,app,updated",
            orderby=None,
            search=None,
            limit=2,
            offset=0,
        ),
    )
    data = response.get("data", [])
    if not data:
        return

    existing = data[0] if isinstance(data[0], dict) else {}
    existing_node_id = str(existing.get("node_id") or "").strip()
    suffix = f" existing node_id={existing_node_id}" if existing_node_id else ""
    raise ValueError(
        f"node nodename already exists: {nodename};"
        f" for existing nodes;{suffix}"
    )


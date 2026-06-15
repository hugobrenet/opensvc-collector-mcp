from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get
from opensvc_collector_mcp.core.prechecks import (
    clean_value,
    require_at_least_one_selector,
    require_exactly_one_selector,
    require_identity,
    require_match,
    require_single_row,
)
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
    selectors = require_exactly_one_selector(
        operation,
        {"node_id": node_id, "nodename": nodename},
        selector_kind="node",
    )
    node = await _resolve_node_by_preferred_selector(
        node_id=selectors["node_id"],
        nodename=selectors["nodename"],
        props=props,
        operation=operation,
    )
    require_identity(
        node,
        operation=operation,
        target="node",
        id_field="node_id",
        name_field="nodename",
    )
    return node


async def resolve_node_reference(
    *,
    node_id: str | None = None,
    nodename: str | None = None,
    props: str = DEFAULT_NODE_SELECTOR_PROPS,
    operation: str = "node operation",
    missing_message: str | None = None,
    correlation_message: str = "nodename must match the resolved node_id",
) -> dict[str, Any]:
    selectors = require_at_least_one_selector(
        operation,
        {"node_id": node_id, "nodename": nodename},
        selector_kind="node",
        message=missing_message,
    )
    node = await _resolve_node_by_preferred_selector(
        node_id=selectors["node_id"],
        nodename=selectors["nodename"],
        props=props,
        operation=operation,
    )
    _, resolved_nodename = require_identity(
        node,
        operation=operation,
        target="node",
        id_field="node_id",
        name_field="nodename",
    )
    require_match(
        selectors["nodename"],
        resolved_nodename,
        message=correlation_message,
    )
    return node


async def _resolve_node_by_preferred_selector(
    *,
    node_id: str,
    nodename: str,
    props: str,
    operation: str,
) -> dict[str, Any]:
    if node_id:
        return await _resolve_node_id_selector(
            node_id=node_id,
            props=props,
            operation=operation,
        )
    return await _resolve_nodename_selector(
        nodename=nodename,
        props=props,
        operation=operation,
    )


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
    node = require_single_row(
        response,
        not_found_message=f"{operation} node_id not found: {node_id}",
        multiple_message=f"{operation} node_id resolved to multiple nodes: {node_id}",
        invalid_message=f"{operation} resolved node payload is invalid",
    )

    resolved_node_id = clean_value(node.get("node_id"))
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
    return require_single_row(
        response,
        not_found_message=f"{operation} nodename not found: {nodename}",
        multiple_message=(
            f"{operation} nodename is ambiguous: {nodename}; "
            "retry with node_id from list_nodes"
        ),
        invalid_message=f"{operation} resolved node payload is invalid",
        exact_match_field="nodename",
        exact_match_value=nodename,
    )


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
    existing_node_id = clean_value(existing.get("node_id"))
    suffix = f" existing node_id={existing_node_id}" if existing_node_id else ""
    raise ValueError(
        f"node nodename already exists: {nodename};"
        f" for existing nodes;{suffix}"
    )

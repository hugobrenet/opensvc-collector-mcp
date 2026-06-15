from typing import Any

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


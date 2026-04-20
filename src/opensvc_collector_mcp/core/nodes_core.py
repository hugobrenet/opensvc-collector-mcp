from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get


def list_nodes(props: str | None = None) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if props:
        params["props"] = props
    return collector_get("/nodes", params=params or None)


def get_node(nodename: str) -> dict[str, Any]:
    nodename = nodename.strip()
    if not nodename:
        raise ValueError("nodename must not be empty")

    return collector_get(f"/nodes/{quote(nodename, safe='')}")

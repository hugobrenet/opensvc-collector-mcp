from typing import Any

from opensvc_collector_mcp.client import collector_get


def list_nodes(props: str | None = None) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if props:
        params["props"] = props
    return collector_get("/nodes", params=params or None)

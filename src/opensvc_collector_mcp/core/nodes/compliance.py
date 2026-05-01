from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get_all


async def get_node_compliance(nodename: str) -> dict[str, Any]:
    nodename = nodename.strip()
    if not nodename:
        raise ValueError("nodename must not be empty")

    response = await collector_get_all(
        f"/nodes/{quote(nodename, safe='')}/compliance/status",
    )
    return {
        "nodename": nodename,
        "meta": response.get("meta", {}),
        "data": response.get("data", []),
    }

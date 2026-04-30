from typing import Any
from opensvc_collector_mcp.client import collector_get

from ._common import _empty_to_none


NODE_CLUSTER_PROPS = "nodename,nodes.cluster_id:cluster_id,clusters.cluster_name:cluster_name"


async def get_node_cluster(nodename: str) -> dict[str, Any]:
    nodename = nodename.strip()
    if not nodename:
        raise ValueError("nodename must not be empty")

    response = await collector_get(
        "/nodes",
        params=[
            ("meta", "False"),
            ("props", NODE_CLUSTER_PROPS),
            ("filters", f"nodename={nodename}"),
            ("limit", 1),
            ("offset", 0),
        ],
    )
    data = response.get("data", [])
    row = data[0] if data else {"nodename": nodename}
    cluster_id = _empty_to_none(row.get("cluster_id"))
    cluster_name = _empty_to_none(row.get("cluster_name"))
    return {
        "nodename": nodename,
        "cluster": (
            {
                "id": cluster_id,
                "name": cluster_name,
            }
            if cluster_id or cluster_name
            else None
        ),
        "raw": {
            "nodename": row.get("nodename"),
            "cluster_id": row.get("cluster_id"),
            "cluster_name": row.get("cluster_name"),
        },
    }

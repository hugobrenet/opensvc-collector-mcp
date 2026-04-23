from typing import Any

from opensvc_collector_mcp.client import collector_get


CLUSTER_NODES_PROPS = "nodename,clusters.cluster_name:cluster_name"


async def get_cluster_nodes(cluster_name: str) -> dict[str, Any]:
    cluster_name = cluster_name.strip()
    if not cluster_name:
        raise ValueError("cluster_name must not be empty")

    response = await collector_get(
        "/nodes",
        params=[
            ("meta", "False"),
            ("props", CLUSTER_NODES_PROPS),
            ("filters", f"clusters.cluster_name={cluster_name}"),
        ],
    )
    data = response.get("data", [])
    return {
        "cluster_name": cluster_name,
        "meta": {
            "count": len(data),
            "source": "nodes",
            "filter": {"clusters.cluster_name": cluster_name},
            "included_props": CLUSTER_NODES_PROPS.split(","),
        },
        "data": data,
    }

from typing import Any

from opensvc_collector_mcp.client import collector_get_all


CLUSTER_NODES_PROPS = "nodename,clusters.cluster_name:cluster_name"


async def get_cluster_nodes(cluster_name: str) -> dict[str, Any]:
    cluster_name = cluster_name.strip()
    if not cluster_name:
        raise ValueError("cluster_name must not be empty")

    response = await collector_get_all(
        "/nodes",
        params=[
            ("meta", "False"),
            ("props", CLUSTER_NODES_PROPS),
            ("filters", f"clusters.cluster_name={cluster_name}"),
        ],
        strategy="limit_zero",
    )
    data = response.get("data", [])
    meta = response.get("meta", {})
    return {
        "cluster_name": cluster_name,
        "meta": {
            "count": len(data),
            "total": meta.get("total"),
            "complete": meta.get("complete"),
            "strategy": meta.get("strategy"),
            "source": "nodes",
            "filter": {"clusters.cluster_name": cluster_name},
            "included_props": CLUSTER_NODES_PROPS.split(","),
        },
        "data": data,
    }

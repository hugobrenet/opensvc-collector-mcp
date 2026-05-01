from typing import Any

from opensvc_collector_mcp.client import collector_get
from opensvc_collector_mcp.core.utils import collection_params, parse_collector_filters


CLUSTER_NODES_PROPS = "nodename,clusters.cluster_name:cluster_name"


async def get_cluster_nodes(
    cluster_name: str,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "nodename",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    cluster_name = cluster_name.strip()
    if not cluster_name:
        raise ValueError("cluster_name must not be empty")

    selected_props = props or CLUSTER_NODES_PROPS
    parsed_filters = [
        ("clusters.cluster_name", cluster_name),
        *parse_collector_filters(filters),
    ]
    response = await collector_get(
        "/nodes",
        params=collection_params(
            filters=parsed_filters,
            props=selected_props,
            orderby=orderby,
            search=search,
            limit=limit,
            offset=offset,
        ),
    )
    data = response.get("data", [])
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "nodes",
            "filter": {field: value for field, value in parsed_filters},
            "included_props": selected_props.split(","),
            "output_count": len(data),
        }
    )
    return {"cluster_name": cluster_name, "meta": meta, "data": data}

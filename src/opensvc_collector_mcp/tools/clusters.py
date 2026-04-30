from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from opensvc_collector_mcp.config import TOOL_TIMEOUT_SECONDS
from opensvc_collector_mcp.core.clusters import (
    get_cluster_nodes as core_get_cluster_nodes,
)
from opensvc_collector_mcp.models.clusters import (
    ClusterNameRequest,
    ClusterNodesResponse,
)


def register_clusters_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_cluster_nodes",
        description=(
            "Return OpenSVC Collector nodes that belong to a cluster. "
            "The tool filters /nodes on clusters.cluster_name."
        ),
        tags={"clusters", "nodes", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Cluster Nodes",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_cluster_nodes(
        request: Annotated[
            ClusterNameRequest,
            Field(description="Cluster name used to list member nodes."),
        ],
    ) -> ClusterNodesResponse:
        """Return nodes belonging to one OpenSVC Collector cluster."""
        response = await core_get_cluster_nodes(cluster_name=request.cluster_name)
        return ClusterNodesResponse.model_validate(response)

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from opensvc_collector_mcp.models.nodes_model import (
    CountNodesRequest,
    CountNodesResponse,
    InventoryStatsRequest,
    InventoryStatsResponse,
    ListNodesRequest,
    NodeHealthResponse,
    NodeNameRequest,
    NodePropsResponse,
    NodeRowsResponse,
    SearchNodesRequest,
)
from opensvc_collector_mcp.core.nodes_core import (
    count_nodes as core_count_nodes,
    get_node as core_get_node,
    get_node_health as core_get_node_health,
    get_nodes_inventory_stats as core_get_nodes_inventory_stats,
    list_node_props as core_list_node_props,
    list_nodes as core_list_nodes,
    search_nodes as core_search_nodes,
)


def register_nodes_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        name="list_nodes",
        description=(
            "List nodes from the OpenSVC Collector inventory. "
            "Use the optional props argument to limit the returned fields "
            "and reduce response size."
        ),
        tags={"nodes", "inventory", "read"},
        annotations={
            "title": "List OpenSVC Nodes",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def list_nodes(
        request: Annotated[
            ListNodesRequest,
            Field(description="Optional node listing parameters."),
        ] = ListNodesRequest(),
    ) -> NodeRowsResponse:
        """Return OpenSVC Collector nodes and their selected properties."""
        response = await core_list_nodes(props=request.props)
        return NodeRowsResponse.model_validate(response)

    @mcp.tool(
        name="list_node_props",
        description=(
            "List available OpenSVC Collector node properties. "
            "Use this before list_nodes or search tools to choose valid props."
        ),
        tags={"nodes", "inventory", "schema", "read"},
        annotations={
            "title": "List OpenSVC Node Properties",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def list_node_props() -> NodePropsResponse:
        """Return the available node properties exposed by the Collector."""
        response = await core_list_node_props()
        return NodePropsResponse.model_validate(response)

    @mcp.tool(
        name="search_nodes",
        description=(
            "Search OpenSVC Collector nodes using exact-match inventory filters. "
            "Use nodename_contains for a case-insensitive nodename substring search."
        ),
        tags={"nodes", "inventory", "search", "read"},
        annotations={
            "title": "Search OpenSVC Nodes",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def search_nodes(
        request: Annotated[
            SearchNodesRequest,
            Field(
                description=(
                    "Search criteria, pagination, and returned properties for "
                    "node inventory lookup."
                ),
            ),
        ],
    ) -> NodeRowsResponse:
        """Search nodes by common inventory fields."""
        response = await core_search_nodes(
            filters=request.merged_filters(),
            nodename_contains=request.nodename_contains,
            props=request.props,
            limit=request.limit,
            offset=request.offset,
            max_scan=request.max_scan,
        )
        return NodeRowsResponse.model_validate(response)

    @mcp.tool(
        name="count_nodes",
        description=(
            "Count OpenSVC Collector nodes matching exact-match inventory filters. "
            "Use this for questions like how many nodes are down, in prod, "
            "or warn in Paris."
        ),
        tags={"nodes", "inventory", "count", "read"},
        annotations={
            "title": "Count OpenSVC Nodes",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def count_nodes(
        request: Annotated[
            CountNodesRequest,
            Field(description="Exact-match filters used to count Collector nodes."),
        ],
    ) -> CountNodesResponse:
        """Return the number of nodes matching the provided filters."""
        response = await core_count_nodes(filters=request.merged_filters())
        return CountNodesResponse.model_validate(response)

    @mcp.tool(
        name="get_node",
        description=(
            "Return all available OpenSVC Collector information for one node. "
            "The node is selected by its exact nodename."
        ),
        tags={"nodes", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Node",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_node(
        request: Annotated[
            NodeNameRequest,
            Field(description="Node identifier used to retrieve full Collector details."),
        ],
    ) -> NodeRowsResponse:
        """Return all available properties for one OpenSVC Collector node."""
        response = await core_get_node(nodename=request.nodename)
        return NodeRowsResponse.model_validate(response)

    @mcp.tool(
        name="get_node_health",
        description=(
            "Return a health-oriented summary for one OpenSVC Collector node. "
            "The result interprets status, maintenance, frozen state, alert dates, "
            "and communication timestamps."
        ),
        tags={"nodes", "inventory", "health", "read"},
        annotations={
            "title": "Get OpenSVC Node Health",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_node_health(
        request: Annotated[
            NodeNameRequest,
            Field(description="Node identifier used to evaluate node health."),
        ],
    ) -> NodeHealthResponse:
        """Return health signals and interpreted issues for one node."""
        response = await core_get_node_health(nodename=request.nodename)
        return NodeHealthResponse.model_validate(response)

    @mcp.tool(
        name="get_nodes_inventory_stats",
        description=(
            "Return aggregate counts over OpenSVC Collector nodes. "
            "Use this for questions about possible values or counts by status, "
            "asset_env, node_env, location, app, or operating system."
        ),
        tags={"nodes", "inventory", "stats", "read"},
        annotations={
            "title": "Get OpenSVC Nodes Inventory Stats",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_nodes_inventory_stats(
        request: Annotated[
            InventoryStatsRequest,
            Field(description="Aggregation fields and scan bounds for node inventory stats."),
        ] = InventoryStatsRequest(),
    ) -> InventoryStatsResponse:
        """Return aggregate node inventory counts."""
        response = await core_get_nodes_inventory_stats(
            fields=request.fields,
            page_size=request.page_size,
            max_nodes=request.max_nodes,
        )
        return InventoryStatsResponse.model_validate(response)

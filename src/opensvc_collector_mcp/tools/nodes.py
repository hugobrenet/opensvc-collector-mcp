from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from opensvc_collector_mcp.models.nodes_model import (
    CountNodesRequest,
    CountNodesResponse,
    InventoryStatsRequest,
    InventoryStatsResponse,
    ListNodesRequest,
    NodeClusterResponse,
    NodeHardwareResponse,
    NodeHealthResponse,
    NodeLocationResponse,
    NodeNameRequest,
    NodeNetworkResponse,
    NodesByTagResponse,
    NodesWithoutTagResponse,
    NodeOrganizationResponse,
    NodeOsResponse,
    NodePropsResponse,
    NodeRowsResponse,
    NodeServicesResponse,
    NodeTagsResponse,
    SearchNodesRequest,
    TagNameRequest,
)
from opensvc_collector_mcp.core.nodes_core import (
    count_nodes as core_count_nodes,
    get_node as core_get_node,
    get_node_cluster as core_get_node_cluster,
    get_node_hardware as core_get_node_hardware,
    get_node_health as core_get_node_health,
    get_node_location as core_get_node_location,
    get_node_network as core_get_node_network,
    get_node_organization as core_get_node_organization,
    get_node_os as core_get_node_os,
    get_node_services as core_get_node_services,
    get_node_tags as core_get_node_tags,
    get_nodes_inventory_stats as core_get_nodes_inventory_stats,
    list_node_props as core_list_node_props,
    list_nodes as core_list_nodes,
    search_node_by_tag as core_search_node_by_tag,
    search_nodes_without_tag as core_search_nodes_without_tag,
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
        name="get_node_tags",
        description=(
            "Return tags attached to one OpenSVC Collector node. "
            "The node is selected by its exact nodename."
        ),
        tags={"nodes", "tags", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Node Tags",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_node_tags(
        request: Annotated[
            NodeNameRequest,
            Field(description="Node identifier used to list attached tags."),
        ],
    ) -> NodeTagsResponse:
        """Return tags attached to one OpenSVC Collector node."""
        nodename = request.nodename.strip()
        response = await core_get_node_tags(nodename=nodename)
        return NodeTagsResponse.model_validate({"nodename": nodename, **response})

    @mcp.tool(
        name="search_node_by_tag",
        description=(
            "Return nodes attached to one OpenSVC Collector tag. "
            "The tool resolves the tag id from the exact tag name, then calls "
            "/tags/<tag_id>/nodes."
        ),
        tags={"nodes", "tags", "search", "read"},
        annotations={
            "title": "Search Nodes By Tag",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def search_node_by_tag(
        request: Annotated[
            TagNameRequest,
            Field(description="Exact tag name used to list attached nodes."),
        ],
    ) -> NodesByTagResponse:
        """Return nodes attached to one OpenSVC Collector tag."""
        response = await core_search_node_by_tag(tag_name=request.tag_name)
        return NodesByTagResponse.model_validate(response)

    @mcp.tool(
        name="search_nodes_without_tag",
        description=(
            "Return nodes that do not have one OpenSVC Collector tag attached. "
            "The tool resolves the tag id, lists tagged nodes, then returns the "
            "difference against all Collector nodes."
        ),
        tags={"nodes", "tags", "search", "read"},
        annotations={
            "title": "Search Nodes Without Tag",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def search_nodes_without_tag(
        request: Annotated[
            TagNameRequest,
            Field(description="Exact tag name used to exclude tagged nodes."),
        ],
    ) -> NodesWithoutTagResponse:
        """Return nodes that do not have one OpenSVC Collector tag attached."""
        response = await core_search_nodes_without_tag(tag_name=request.tag_name)
        return NodesWithoutTagResponse.model_validate(response)

    @mcp.tool(
        name="get_node_location",
        description=(
            "Return location fields for one OpenSVC Collector node. "
            "The node is selected by its exact nodename."
        ),
        tags={"nodes", "location", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Node Location",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_node_location(
        request: Annotated[
            NodeNameRequest,
            Field(description="Node identifier used to retrieve location fields."),
        ],
    ) -> NodeLocationResponse:
        """Return location details for one OpenSVC Collector node."""
        response = await core_get_node_location(nodename=request.nodename)
        return NodeLocationResponse.model_validate(response)

    @mcp.tool(
        name="get_node_organization",
        description=(
            "Return organization fields for one OpenSVC Collector node: "
            "responsible team, integration team, support team, and application."
        ),
        tags={"nodes", "organization", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Node Organization",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_node_organization(
        request: Annotated[
            NodeNameRequest,
            Field(description="Node identifier used to retrieve organization fields."),
        ],
    ) -> NodeOrganizationResponse:
        """Return organization details for one OpenSVC Collector node."""
        response = await core_get_node_organization(nodename=request.nodename)
        return NodeOrganizationResponse.model_validate(response)

    @mcp.tool(
        name="get_node_hardware",
        description=(
            "Return hardware inventory fields for one OpenSVC Collector node: "
            "identity, CPU, memory, power, and hardware placement."
        ),
        tags={"nodes", "hardware", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Node Hardware",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_node_hardware(
        request: Annotated[
            NodeNameRequest,
            Field(description="Node identifier used to retrieve hardware inventory fields."),
        ],
    ) -> NodeHardwareResponse:
        """Return hardware inventory details for one OpenSVC Collector node."""
        response = await core_get_node_hardware(nodename=request.nodename)
        return NodeHardwareResponse.model_validate(response)

    @mcp.tool(
        name="get_node_os",
        description=(
            "Return operating system fields for one OpenSVC Collector node: "
            "OS name, vendor, release, kernel, architecture, and runtime metadata."
        ),
        tags={"nodes", "os", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Node OS",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_node_os(
        request: Annotated[
            NodeNameRequest,
            Field(description="Node identifier used to retrieve operating system fields."),
        ],
    ) -> NodeOsResponse:
        """Return operating system details for one OpenSVC Collector node."""
        response = await core_get_node_os(nodename=request.nodename)
        return NodeOsResponse.model_validate(response)

    @mcp.tool(
        name="get_node_network",
        description=(
            "Return network addresses and attached network properties for one "
            "OpenSVC Collector node."
        ),
        tags={"nodes", "network", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Node Network",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_node_network(
        request: Annotated[
            NodeNameRequest,
            Field(description="Node identifier used to retrieve network addresses."),
        ],
    ) -> NodeNetworkResponse:
        """Return network addresses for one OpenSVC Collector node."""
        response = await core_get_node_network(nodename=request.nodename)
        return NodeNetworkResponse.model_validate(response)

    @mcp.tool(
        name="get_node_cluster",
        description=(
            "Return the cluster associated with one OpenSVC Collector node. "
            "The tool reads nodes.cluster_id and joins clusters.cluster_name "
            "through the Collector /nodes endpoint."
        ),
        tags={"nodes", "clusters", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Node Cluster",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_node_cluster(
        request: Annotated[
            NodeNameRequest,
            Field(description="Node identifier used to retrieve the associated cluster."),
        ],
    ) -> NodeClusterResponse:
        """Return cluster id and name for one OpenSVC Collector node."""
        response = await core_get_node_cluster(nodename=request.nodename)
        return NodeClusterResponse.model_validate(response)

    @mcp.tool(
        name="get_node_services",
        description=(
            "Return service instances hosted on one OpenSVC Collector node. "
            "The tool reads /services_instances filtered by nodes.nodename."
        ),
        tags={"nodes", "services", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Node Services",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_node_services(
        request: Annotated[
            NodeNameRequest,
            Field(
                description=(
                    "Node identifier used to list service instances hosted on this node "
                    "through Collector /services_instances."
                ),
            ),
        ],
    ) -> NodeServicesResponse:
        """Return service instances hosted on one OpenSVC Collector node."""
        response = await core_get_node_services(nodename=request.nodename)
        return NodeServicesResponse.model_validate(response)

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

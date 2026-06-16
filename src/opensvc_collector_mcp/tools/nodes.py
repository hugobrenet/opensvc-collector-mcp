from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from opensvc_collector_mcp.config import TOOL_TIMEOUT_SECONDS
from opensvc_collector_mcp.models.nodes import (
    CountNodesRequest,
    CountNodesResponse,
    CreateNodeRequest,
    CreateNodeResponse,
    DeleteNodeRequest,
    DeleteNodeResponse,
    FreezeNodeRequest,
    FreezeNodeResponse,
    ThawNodeRequest,
    ThawNodeResponse,
    InventoryStatsRequest,
    InventoryStatsResponse,
    ListNodesRequest,
    NodeClusterResponse,
    NodeChecksResponse,
    NodeComplianceResponse,
    NodeDisksResponse,
    NodeHardwareResponse,
    NodeHealthResponse,
    NodeLocationResponse,
    NodeNameRequest,
    NodeRelationRequest,
    NodeNetworkResponse,
    NodeOrganizationResponse,
    NodeOsResponse,
    NodePropsResponse,
    NodeRowsResponse,
    NodeServicesRequest,
    NodeServicesResponse,
    NodeTagsResponse,
    SnoozeNodeNotificationsRequest,
    SnoozeNodeNotificationsResponse,
    UnsnoozeNodeNotificationsRequest,
    UnsnoozeNodeNotificationsResponse,
    UpdateNodePropertiesRequest,
    UpdateNodePropertiesResponse,
)
from opensvc_collector_mcp.core.nodes import (
    count_nodes as core_count_nodes,
    create_node as core_create_node,
    delete_node as core_delete_node,
    freeze_node as core_freeze_node,
    thaw_node as core_thaw_node,
    get_node as core_get_node,
    get_node_cluster as core_get_node_cluster,
    get_node_checks as core_get_node_checks,
    get_node_compliance as core_get_node_compliance,
    get_node_disks as core_get_node_disks,
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
    snooze_node_notifications as core_snooze_node_notifications,
    unsnooze_node_notifications as core_unsnooze_node_notifications,
    update_node_properties as core_update_node_properties,
)


def register_nodes_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="create_node",
        description=(
            "Create or submit one OpenSVC Collector node through POST /nodes. "
            "MCP first checks that no existing node has the exact nodename, "
            "because Collector POST /nodes otherwise behaves like an upsert. "
            "Collector remains the final authority for defaults such as "
            "team_responsible and payload validation. Before calling, ask "
            "the user to repeat an exact confirmation phrase and include it in "
            "request.confirmation.phrase. Requires Collector NodeManager or "
            "Manager privileges through MCP RBAC."
        ),
        tags={"nodes", "create", "write:nodes"},
        annotations={
            "title": "Create OpenSVC Node",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": True,
            "openWorldHint": False,
        },
    )
    async def create_node(
        request: Annotated[
            CreateNodeRequest,
            Field(description="Node creation payload and confirmation."),
        ],
    ) -> CreateNodeResponse:
        """Submit an OpenSVC Collector node creation request."""
        response = await core_create_node(
            nodename=request.nodename,
            properties=request.properties,
        )
        return CreateNodeResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="delete_node",
        description=(
            "Delete one OpenSVC Collector node selected by exact node_id or "
            "exact nodename. MCP resolves nodename to one node_id and refuses "
            "missing or ambiguous duplicate nodenames. Before calling, ask the "
            "user to repeat an exact confirmation phrase containing the resolved "
            "node_id and nodename, and include it in request.confirmation.phrase. "
            "Requires confirm_node_id, confirm_nodename, and Collector "
            "NodeManager or Manager privileges through MCP RBAC."
        ),
        tags={"nodes", "delete", "delete:nodes"},
        annotations={
            "title": "Delete OpenSVC Node",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": True,
            "openWorldHint": False,
        },
    )
    async def delete_node(
        request: Annotated[
            DeleteNodeRequest,
            Field(description="Node deletion selector and explicit confirmations."),
        ],
    ) -> DeleteNodeResponse:
        "Delete an OpenSVC Collector node after explicit id and name confirmation."
        response = await core_delete_node(
            node_id=request.node_id,
            nodename=request.nodename,
            confirm_node_id=request.confirm_node_id,
            confirm_nodename=request.confirm_nodename,
        )
        return DeleteNodeResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="freeze_node",
        description=(
            "Enqueue a freeze action for one OpenSVC Collector node through "
            "PUT /actions with action=freeze and the resolved node_id. Accepts "
            "either exact node_id or exact nodename; MCP resolves nodename to "
            "one node_id, refuses ambiguous matches, and verifies explicit "
            "confirm_node_id and confirm_nodename before enqueueing the action. "
            "Before calling, ask the user to repeat an exact confirmation phrase "
            "containing the resolved node_id and nodename, and include it in "
            "request.confirmation.phrase. Requires Collector NodeExec or Manager "
            "privileges through MCP RBAC."
        ),
        tags={"nodes", "freeze", "exec:nodes"},
        annotations={
            "title": "Freeze OpenSVC Node",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": True,
            "openWorldHint": False,
        },
    )
    async def freeze_node(
        request: Annotated[
            FreezeNodeRequest,
            Field(description="Node freeze selector and explicit confirmations."),
        ],
    ) -> FreezeNodeResponse:
        """Enqueue a freeze action for one OpenSVC Collector node."""
        response = await core_freeze_node(
            node_id=request.node_id,
            nodename=request.nodename,
            confirm_node_id=request.confirm_node_id,
            confirm_nodename=request.confirm_nodename,
        )
        return FreezeNodeResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="thaw_node",
        description=(
            "Enqueue a thaw/unfreeze action for one OpenSVC Collector node "
            "through PUT /actions with action=thaw and the resolved node_id. "
            "Accepts either exact node_id or exact nodename; MCP resolves "
            "nodename to one node_id, refuses ambiguous matches, and verifies "
            "explicit confirm_node_id and confirm_nodename before enqueueing "
            "the action. Before calling, ask the user to repeat an exact "
            "confirmation phrase containing the resolved node_id and nodename, "
            "and include it in request.confirmation.phrase. Requires Collector "
            "NodeExec or Manager privileges through MCP RBAC."
        ),
        tags={"nodes", "thaw", "exec:nodes"},
        annotations={
            "title": "Thaw OpenSVC Node",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": True,
            "openWorldHint": False,
        },
    )
    async def thaw_node(
        request: Annotated[
            ThawNodeRequest,
            Field(description="Node thaw selector and explicit confirmations."),
        ],
    ) -> ThawNodeResponse:
        """Enqueue a thaw action for one OpenSVC Collector node."""
        response = await core_thaw_node(
            node_id=request.node_id,
            nodename=request.nodename,
            confirm_node_id=request.confirm_node_id,
            confirm_nodename=request.confirm_nodename,
        )
        return ThawNodeResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="update_node_properties",
        description=(
            "Update Collector-writable properties on one existing OpenSVC "
            "Collector node selected by exact nodename. Before calling, ask "
            "the user to repeat an exact confirmation phrase and include it in "
            "request.confirmation.phrase. Requires Collector NodeManager or "
            "Manager privileges through MCP RBAC."
        ),
        tags={"nodes", "update", "write:nodes"},
        annotations={
            "title": "Update OpenSVC Node Properties",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": True,
            "openWorldHint": False,
        },
    )
    async def update_node_properties(
        request: Annotated[
            UpdateNodePropertiesRequest,
            Field(description="Node property update parameters."),
        ],
    ) -> UpdateNodePropertiesResponse:
        """Update Collector-writable node properties."""
        response = await core_update_node_properties(
            nodename=request.nodename,
            properties=request.properties,
        )
        return UpdateNodePropertiesResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="snooze_node_notifications",
        description=(
            "Snooze notifications on one OpenSVC Collector node through "
            "POST /nodes/<node_id>/snooze with duration. Accepts either exact "
            "node_id or exact nodename; MCP resolves nodename to a single node_id "
            "and refuses ambiguous duplicate nodenames. Before calling, ask the "
            "user to repeat an exact confirmation phrase and include it in "
            "request.confirmation.phrase. Requires Collector NodeManager or "
            "Manager privileges through MCP RBAC."
        ),
        tags={"nodes", "snooze", "write:nodes"},
        annotations={
            "title": "Snooze OpenSVC Node Notifications",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": False,
            "openWorldHint": False,
        },
    )
    async def snooze_node_notifications(
        request: Annotated[
            SnoozeNodeNotificationsRequest,
            Field(description="Node notification snooze selector and duration."),
        ],
    ) -> SnoozeNodeNotificationsResponse:
        """Snooze notifications on one Collector node."""
        response = await core_snooze_node_notifications(
            node_id=request.node_id,
            nodename=request.nodename,
            duration=request.duration,
        )
        return SnoozeNodeNotificationsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="unsnooze_node_notifications",
        description=(
            "Unsnooze notifications on one OpenSVC Collector node through "
            "POST /nodes/<node_id>/snooze without duration. Accepts either "
            "exact node_id or exact nodename; MCP resolves nodename to a single "
            "node_id and refuses ambiguous duplicate nodenames. Before calling, "
            "ask the user to repeat an exact confirmation phrase and include it "
            "in request.confirmation.phrase. Requires Collector NodeManager or "
            "Manager privileges through MCP RBAC."
        ),
        tags={"nodes", "unsnooze", "write:nodes"},
        annotations={
            "title": "Unsnooze OpenSVC Node Notifications",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": False,
            "openWorldHint": False,
        },
    )
    async def unsnooze_node_notifications(
        request: Annotated[
            UnsnoozeNodeNotificationsRequest,
            Field(description="Node notification unsnooze selector."),
        ],
    ) -> UnsnoozeNodeNotificationsResponse:
        """Unsnooze notifications on one Collector node."""
        response = await core_unsnooze_node_notifications(
            node_id=request.node_id,
            nodename=request.nodename,
        )
        return UnsnoozeNodeNotificationsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="list_nodes",
        description=(
            "List or search nodes from the OpenSVC Collector inventory. "
            "Use filters for exact-match lookup, search for Collector full-text "
            "search, nodename_contains for partial nodename lookup, and props "
            "to reduce response size. Do not use this tool to compute global "
            "node inventory statistics, summaries, distributions, or counts by "
            "category; use get_nodes_inventory_stats instead."
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
        response = await core_list_nodes(
            filters=request.merged_filters(),
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            limit=request.limit,
            offset=request.offset,
            nodename_contains=request.nodename_contains,
            max_scan=request.max_scan,
        )
        return NodeRowsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="list_node_props",
        description=(
            "List available OpenSVC Collector node properties. "
            "Use this before list_nodes to choose valid filters and props."
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
        timeout=TOOL_TIMEOUT_SECONDS,
        name="count_nodes",
        description=(
            "Count OpenSVC Collector nodes matching exact-match inventory filters. "
            "Use this for questions like how many nodes are down, in lab, "
            "or warn in Lab City."
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
        timeout=TOOL_TIMEOUT_SECONDS,
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
            Field(
                description="Node identifier used to retrieve full Collector details."
            ),
        ],
    ) -> NodeRowsResponse:
        """Return all available properties for one OpenSVC Collector node."""
        response = await core_get_node(nodename=request.nodename)
        return NodeRowsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
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
            NodeRelationRequest,
            Field(description="Node identifier used to list attached tags."),
        ],
    ) -> NodeTagsResponse:
        """Return tags attached to one OpenSVC Collector node."""
        nodename = request.nodename.strip()
        response = await core_get_node_tags(
            nodename=nodename,
            filters=request.merged_filters(),
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            limit=request.limit,
            offset=request.offset,
        )
        return NodeTagsResponse.model_validate({"nodename": nodename, **response})

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
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
        timeout=TOOL_TIMEOUT_SECONDS,
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
        timeout=TOOL_TIMEOUT_SECONDS,
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
            Field(
                description="Node identifier used to retrieve hardware inventory fields."
            ),
        ],
    ) -> NodeHardwareResponse:
        """Return hardware inventory details for one OpenSVC Collector node."""
        response = await core_get_node_hardware(nodename=request.nodename)
        return NodeHardwareResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
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
            Field(
                description="Node identifier used to retrieve operating system fields."
            ),
        ],
    ) -> NodeOsResponse:
        """Return operating system details for one OpenSVC Collector node."""
        response = await core_get_node_os(nodename=request.nodename)
        return NodeOsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
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
            NodeRelationRequest,
            Field(description="Node identifier used to retrieve network addresses."),
        ],
    ) -> NodeNetworkResponse:
        """Return network addresses for one OpenSVC Collector node."""
        response = await core_get_node_network(
            nodename=request.nodename,
            filters=request.merged_filters(),
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            limit=request.limit,
            offset=request.offset,
        )
        return NodeNetworkResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_node_compliance",
        description=(
            "Return compliance execution status rows for one OpenSVC Collector node."
        ),
        tags={"nodes", "compliance", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Node Compliance",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_node_compliance(
        request: Annotated[
            NodeRelationRequest,
            Field(
                description="Node identifier used to retrieve compliance status rows."
            ),
        ],
    ) -> NodeComplianceResponse:
        """Return compliance status rows for one OpenSVC Collector node."""
        response = await core_get_node_compliance(
            nodename=request.nodename,
            filters=request.merged_filters(),
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            limit=request.limit,
            offset=request.offset,
        )
        return NodeComplianceResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_node_checks",
        description=(
            "Return live check result rows for one OpenSVC Collector node. "
            "Use this for threshold-based checks such as values, errors, and "
            "high or low limits reported on the node."
        ),
        tags={"nodes", "checks", "health", "read"},
        annotations={
            "title": "Get OpenSVC Node Checks",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_node_checks(
        request: Annotated[
            NodeRelationRequest,
            Field(
                description="Node identifier used to retrieve live check result rows."
            ),
        ],
    ) -> NodeChecksResponse:
        """Return live check result rows for one OpenSVC Collector node."""
        response = await core_get_node_checks(
            nodename=request.nodename,
            filters=request.merged_filters(),
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            limit=request.limit,
            offset=request.offset,
        )
        return NodeChecksResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_node_disks",
        description=(
            "Return disk inventory rows for one OpenSVC Collector node. "
            "Use this for storage inventory, allocation, RAID, and backing array "
            "information exposed by the Collector."
        ),
        tags={"nodes", "storage", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Node Disks",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_node_disks(
        request: Annotated[
            NodeRelationRequest,
            Field(description="Node identifier used to retrieve disk inventory rows."),
        ],
    ) -> NodeDisksResponse:
        """Return disk inventory rows for one OpenSVC Collector node."""
        response = await core_get_node_disks(
            nodename=request.nodename,
            filters=request.merged_filters(),
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            limit=request.limit,
            offset=request.offset,
        )
        return NodeDisksResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
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
            Field(
                description="Node identifier used to retrieve the associated cluster."
            ),
        ],
    ) -> NodeClusterResponse:
        """Return cluster id and name for one OpenSVC Collector node."""
        response = await core_get_node_cluster(nodename=request.nodename)
        return NodeClusterResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
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
            NodeServicesRequest,
            Field(
                description=(
                    "Node identifier used to list service instances hosted on this node "
                    "through Collector /services_instances."
                ),
            ),
        ],
    ) -> NodeServicesResponse:
        """Return service instances hosted on one OpenSVC Collector node."""
        response = await core_get_node_services(
            nodename=request.nodename,
            filters=request.merged_filters(),
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            limit=request.limit,
            offset=request.offset,
        )
        return NodeServicesResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
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
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_nodes_inventory_stats",
        description=(
            "Return aggregate counts over OpenSVC Collector nodes. "
            "Use this for node inventory statistics, statistical summaries, "
            "aggregated summaries, distributions, possible values, or counts by "
            "status, asset_env, node_env, location, app, or operating system. "
            "Prefer this tool over list_nodes when the user asks for a summary, "
            "stats, distribution, or aggregated inventory."
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
            Field(
                description="Aggregation fields and scan bounds for node inventory stats."
            ),
        ] = InventoryStatsRequest(),
    ) -> InventoryStatsResponse:
        """Return aggregate node inventory counts."""
        response = await core_get_nodes_inventory_stats(
            fields=request.fields,
            max_nodes=request.max_nodes,
        )
        return InventoryStatsResponse.model_validate(response)

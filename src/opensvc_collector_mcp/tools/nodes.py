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
    RunNodeChecksRequest,
    RunNodeChecksResponse,
    CollectNodeSysreportRequest,
    CollectNodeSysreportResponse,
    PushNodeAssetRequest,
    PushNodeAssetResponse,
    PushNodeDisksRequest,
    PushNodeDisksResponse,
    PushNodePackagesRequest,
    PushNodePackagesResponse,
    PushNodePatchesRequest,
    PushNodePatchesResponse,
    PushNodeStatsRequest,
    PushNodeStatsResponse,
    PullNodeConfigRequest,
    PullNodeConfigResponse,
    PushNodeConfigRequest,
    PushNodeConfigResponse,
    UpdateNodeComplianceModulesRequest,
    UpdateNodeComplianceModulesResponse,
    UpdateNodeOpensvcAgentRequest,
    UpdateNodeOpensvcAgentResponse,
    ScanNodeScsiRequest,
    ScanNodeScsiResponse,
    RebootNodeRequest,
    RebootNodeResponse,
    ScheduleNodeRebootRequest,
    ScheduleNodeRebootResponse,
    UnscheduleNodeRebootRequest,
    UnscheduleNodeRebootResponse,
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
    run_node_checks as core_run_node_checks,
    collect_node_sysreport as core_collect_node_sysreport,
    push_node_asset as core_push_node_asset,
    push_node_disks as core_push_node_disks,
    push_node_packages as core_push_node_packages,
    push_node_patches as core_push_node_patches,
    push_node_stats as core_push_node_stats,
    pull_node_config as core_pull_node_config,
    push_node_config as core_push_node_config,
    update_node_compliance_modules as core_update_node_compliance_modules,
    update_node_opensvc_agent as core_update_node_opensvc_agent,
    scan_node_scsi as core_scan_node_scsi,
    reboot_node as core_reboot_node,
    schedule_node_reboot as core_schedule_node_reboot,
    unschedule_node_reboot as core_unschedule_node_reboot,
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
            "Delete one OpenSVC Collector node. Destructive and node_id-only. "
            "If the user gives a nodename, first call get_node to resolve exactly "
            "one node and read its node_id and nodename. Do not ask for a delete "
            "confirmation before this resolution step. Then ask the user to repeat "
            "an exact phrase containing both resolved values, for example: "
            "DELETE node <node_id> <nodename>. When the latest user message "
            "contains that phrase, call delete_node with node_id, confirm_node_id, "
            "confirm_nodename, and request.confirmation.phrase. Do not pass "
            "nodename as an execution selector; use confirm_nodename only for "
            "correlation. Requires Collector NodeManager or Manager privileges "
            "through MCP RBAC."
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
            nodename=None,
            confirm_node_id=request.confirm_node_id,
            confirm_nodename=request.confirm_nodename,
        )
        return DeleteNodeResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="freeze_node",
        description=(
            "Enqueue a freeze action for one OpenSVC Collector node through "
            "PUT /actions with action=freeze. Destructive and node_id-only. "
            "If the user gives a nodename, first call get_node to resolve exactly "
            "one node and read its node_id and nodename. Do not ask for a runtime "
            "action confirmation before this resolution step. Then ask the user "
            "to repeat an exact phrase containing both resolved values, for "
            "example: FREEZE node <node_id> <nodename>. When the latest user "
            "message contains that phrase, call freeze_node with node_id, "
            "confirm_node_id, confirm_nodename, and request.confirmation.phrase. "
            "Do not pass nodename as an execution selector; use confirm_nodename "
            "only for correlation. Requires Collector NodeExec or Manager "
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
            nodename=None,
            confirm_node_id=request.confirm_node_id,
            confirm_nodename=request.confirm_nodename,
        )
        return FreezeNodeResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="thaw_node",
        description=(
            "Enqueue a thaw/unfreeze action for one OpenSVC Collector node "
            "through PUT /actions with action=thaw. Destructive and node_id-only. "
            "If the user gives a nodename, first call get_node to resolve exactly "
            "one node and read its node_id and nodename. Do not ask for a runtime "
            "action confirmation before this resolution step. Then ask the user "
            "to repeat an exact phrase containing both resolved values, for "
            "example: THAW node <node_id> <nodename>. When the latest user "
            "message contains that phrase, call thaw_node with node_id, "
            "confirm_node_id, confirm_nodename, and request.confirmation.phrase. "
            "Do not pass nodename as an execution selector; use confirm_nodename "
            "only for correlation. Requires Collector NodeExec or Manager "
            "privileges through MCP RBAC."
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
            nodename=None,
            confirm_node_id=request.confirm_node_id,
            confirm_nodename=request.confirm_nodename,
        )
        return ThawNodeResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="run_node_checks",
        description=(
            "Enqueue an OpenSVC checks action for one Collector node through "
            "PUT /actions with action=checks. This tool is node_id-only. If the "
            "user gives a nodename, first call get_node to resolve exactly one "
            "node and read its node_id and nodename. Do not ask for a runtime "
            "action confirmation before this resolution step. Then ask the user "
            "to repeat an exact phrase containing both resolved values, for "
            "example: RUN checks node <node_id> <nodename>. When the latest user "
            "message contains that phrase, call run_node_checks with node_id, "
            "confirm_node_id, confirm_nodename, and request.confirmation.phrase. "
            "Do not pass nodename as an execution selector; use confirm_nodename "
            "only for correlation. Requires Collector NodeExec or Manager "
            "privileges through MCP RBAC."
        ),
        tags={"nodes", "checks", "exec:nodes"},
        annotations={
            "title": "Run OpenSVC Node Checks",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": False,
            "openWorldHint": False,
        },
    )
    async def run_node_checks(
        request: Annotated[
            RunNodeChecksRequest,
            Field(description="Node checks selector and explicit confirmations."),
        ],
    ) -> RunNodeChecksResponse:
        """Enqueue a checks action for one OpenSVC Collector node."""
        response = await core_run_node_checks(
            node_id=request.node_id,
            nodename=None,
            confirm_node_id=request.confirm_node_id,
            confirm_nodename=request.confirm_nodename,
        )
        return RunNodeChecksResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="collect_node_sysreport",
        description=(
            "Enqueue a sysreport collection action for one OpenSVC Collector "
            "node through PUT /actions with action=sysreport. This tool is "
            "node_id-only. If the user gives a nodename, first call get_node to "
            "resolve exactly one node and read its node_id and nodename. Do not "
            "ask for a runtime action confirmation before this resolution step. "
            "Then ask the user to repeat an exact phrase containing both resolved "
            "values, for example: COLLECT sysreport node <node_id> <nodename>. "
            "When the latest user message contains that phrase, call "
            "collect_node_sysreport with node_id, confirm_node_id, "
            "confirm_nodename, and request.confirmation.phrase. Do not pass "
            "nodename as an execution selector; use confirm_nodename only for "
            "correlation. Requires Collector NodeExec or Manager privileges "
            "through MCP RBAC."
        ),
        tags={"nodes", "sysreport", "exec:nodes"},
        annotations={
            "title": "Collect OpenSVC Node Sysreport",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": False,
            "openWorldHint": False,
        },
    )
    async def collect_node_sysreport(
        request: Annotated[
            CollectNodeSysreportRequest,
            Field(description="Node sysreport selector and explicit confirmations."),
        ],
    ) -> CollectNodeSysreportResponse:
        """Enqueue a sysreport action for one OpenSVC Collector node."""
        response = await core_collect_node_sysreport(
            node_id=request.node_id,
            nodename=None,
            confirm_node_id=request.confirm_node_id,
            confirm_nodename=request.confirm_nodename,
        )
        return CollectNodeSysreportResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="push_node_asset",
        description=(
            "Enqueue a node asset inventory refresh for one OpenSVC Collector "
            "node through PUT /actions with action=pushasset. This corresponds "
            "to the Collector UI action 'Update node "
            "information' and asks the OpenSVC agent to push node inventory data "
            "such as asset environment, OS, hardware, location, and runtime "
            "identity fields back to Collector. This tool is node_id-only. If "
            "the user gives a nodename, first call get_node to resolve exactly "
            "one node and read its node_id and nodename. Do not ask for a runtime "
            "action confirmation before this resolution step. Then ask the user "
            "to repeat an exact phrase containing both resolved values, for "
            "example: PUSH asset node <node_id> <nodename>. When the latest user "
            "message contains that phrase, call push_node_asset with node_id, "
            "confirm_node_id, confirm_nodename, and request.confirmation.phrase. "
            "Do not pass nodename as an execution selector; use confirm_nodename "
            "only for correlation. Requires Collector NodeExec or Manager "
            "privileges through MCP RBAC."
        ),
        tags={"nodes", "asset", "exec:nodes"},
        annotations={
            "title": "Push OpenSVC Node Asset Inventory",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": False,
            "openWorldHint": False,
        },
    )
    async def push_node_asset(
        request: Annotated[
            PushNodeAssetRequest,
            Field(description="Node asset push selector and explicit confirmations."),
        ],
    ) -> PushNodeAssetResponse:
        """Enqueue a pushasset action for one OpenSVC Collector node."""
        response = await core_push_node_asset(
            node_id=request.node_id,
            nodename=None,
            confirm_node_id=request.confirm_node_id,
            confirm_nodename=request.confirm_nodename,
        )
        return PushNodeAssetResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="push_node_disks",
        description=(
            "Enqueue a node disk inventory refresh for one OpenSVC Collector "
            "node through PUT /actions with action=pushdisks. This corresponds "
            "to the Collector UI action 'Update disks information' and asks the "
            "OpenSVC agent to push disk/storage inventory data back to Collector. "
            "This tool is node_id-only. If the user gives a nodename, first call "
            "get_node to resolve exactly one node and read its node_id and "
            "nodename. Do not ask for a runtime action confirmation before this "
            "resolution step. Then ask the user to repeat an exact phrase "
            "containing both resolved values, for example: PUSH disks node "
            "<node_id> <nodename>. When the latest user message contains that "
            "phrase, call push_node_disks with node_id, confirm_node_id, "
            "confirm_nodename, and request.confirmation.phrase. Do not pass "
            "nodename as an execution selector; use confirm_nodename only for "
            "correlation. Requires Collector NodeExec or Manager privileges "
            "through MCP RBAC."
        ),
        tags={"nodes", "disks", "exec:nodes"},
        annotations={
            "title": "Push OpenSVC Node Disk Inventory",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": False,
            "openWorldHint": False,
        },
    )
    async def push_node_disks(
        request: Annotated[
            PushNodeDisksRequest,
            Field(description="Node disk push selector and explicit confirmations."),
        ],
    ) -> PushNodeDisksResponse:
        """Enqueue a pushdisks action for one OpenSVC Collector node."""
        response = await core_push_node_disks(
            node_id=request.node_id,
            nodename=None,
            confirm_node_id=request.confirm_node_id,
            confirm_nodename=request.confirm_nodename,
        )
        return PushNodeDisksResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="push_node_packages",
        description=(
            "Enqueue a node installed package inventory refresh for one OpenSVC "
            "Collector node through PUT /actions with action=pushpkg. This "
            "corresponds to the Collector UI action 'Update installed packages "
            "information' and asks the OpenSVC agent to push package inventory "
            "data back to Collector. This tool is node_id-only. If the user "
            "gives a nodename, first call get_node to resolve exactly one node "
            "and read its node_id and nodename. Do not ask for a runtime action "
            "confirmation before this resolution step. Then ask the user to "
            "repeat an exact phrase containing both resolved values, for "
            "example: PUSH packages node <node_id> <nodename>. When the latest "
            "user message contains that phrase, call push_node_packages with "
            "node_id, confirm_node_id, confirm_nodename, and "
            "request.confirmation.phrase. Do not pass nodename as an execution "
            "selector; use confirm_nodename only for correlation. Requires "
            "Collector NodeExec or Manager privileges through MCP RBAC."
        ),
        tags={"nodes", "packages", "exec:nodes"},
        annotations={
            "title": "Push OpenSVC Node Package Inventory",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": False,
            "openWorldHint": False,
        },
    )
    async def push_node_packages(
        request: Annotated[
            PushNodePackagesRequest,
            Field(description="Node package push selector and explicit confirmations."),
        ],
    ) -> PushNodePackagesResponse:
        """Enqueue a pushpkg action for one OpenSVC Collector node."""
        response = await core_push_node_packages(
            node_id=request.node_id,
            nodename=None,
            confirm_node_id=request.confirm_node_id,
            confirm_nodename=request.confirm_nodename,
        )
        return PushNodePackagesResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="push_node_patches",
        description=(
            "Enqueue a node installed patch inventory refresh for one OpenSVC "
            "Collector node through PUT /actions with action=pushpatch. This "
            "corresponds to the Collector UI action 'Update installed patches "
            "information' and asks the OpenSVC agent to push patch inventory "
            "data back to Collector. This tool is node_id-only. If the user "
            "gives a nodename, first call get_node to resolve exactly one node "
            "and read its node_id and nodename. Do not ask for a runtime action "
            "confirmation before this resolution step. Then ask the user to "
            "repeat an exact phrase containing both resolved values, for "
            "example: PUSH patches node <node_id> <nodename>. When the latest "
            "user message contains that phrase, call push_node_patches with "
            "node_id, confirm_node_id, confirm_nodename, and "
            "request.confirmation.phrase. Do not pass nodename as an execution "
            "selector; use confirm_nodename only for correlation. Requires "
            "Collector NodeExec or Manager privileges through MCP RBAC."
        ),
        tags={"nodes", "patches", "exec:nodes"},
        annotations={
            "title": "Push OpenSVC Node Patch Inventory",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": False,
            "openWorldHint": False,
        },
    )
    async def push_node_patches(
        request: Annotated[
            PushNodePatchesRequest,
            Field(description="Node patch push selector and explicit confirmations."),
        ],
    ) -> PushNodePatchesResponse:
        """Enqueue a pushpatch action for one OpenSVC Collector node."""
        response = await core_push_node_patches(
            node_id=request.node_id,
            nodename=None,
            confirm_node_id=request.confirm_node_id,
            confirm_nodename=request.confirm_nodename,
        )
        return PushNodePatchesResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="push_node_stats",
        description=(
            "Enqueue a node statistics refresh for one OpenSVC Collector node "
            "through PUT /actions with action=pushstats. This corresponds to "
            "the Collector UI action 'Update stats' and asks the OpenSVC agent "
            "to push node statistics back to Collector. This tool is "
            "node_id-only. If the user gives a nodename, first call get_node to "
            "resolve exactly one node and read its node_id and nodename. Do not "
            "ask for a runtime action confirmation before this resolution step. "
            "Then ask the user to repeat an exact phrase containing both resolved "
            "values, for example: PUSH stats node <node_id> <nodename>. When the "
            "latest user message contains that phrase, call push_node_stats with "
            "node_id, confirm_node_id, confirm_nodename, and "
            "request.confirmation.phrase. Do not pass nodename as an execution "
            "selector; use confirm_nodename only for correlation. Requires "
            "Collector NodeExec or Manager privileges through MCP RBAC."
        ),
        tags={"nodes", "stats", "exec:nodes"},
        annotations={
            "title": "Push OpenSVC Node Statistics",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": False,
            "openWorldHint": False,
        },
    )
    async def push_node_stats(
        request: Annotated[
            PushNodeStatsRequest,
            Field(description="Node stats push selector and explicit confirmations."),
        ],
    ) -> PushNodeStatsResponse:
        """Enqueue a pushstats action for one OpenSVC Collector node."""
        response = await core_push_node_stats(
            node_id=request.node_id,
            nodename=None,
            confirm_node_id=request.confirm_node_id,
            confirm_nodename=request.confirm_nodename,
        )
        return PushNodeStatsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="pull_node_config",
        description=(
            "Enqueue a node-only OpenSVC configuration pull action for one "
            "Collector node through PUT /actions with action=pull. This queues "
            "the Collector node action handled as nodemgr pull for the resolved "
            "node_id. It is not the future service-instance Pull tool and does "
            "not take svc_id. This tool is node_id-only. If the user gives a "
            "nodename, first call get_node to resolve exactly one node and read "
            "its node_id and nodename. Do not ask for a runtime action "
            "confirmation before this resolution step. Then ask the user to "
            "repeat an exact phrase containing both resolved values, for "
            "example: PULL config node <node_id> <nodename>. When the latest "
            "user message contains that phrase, call pull_node_config with "
            "node_id, confirm_node_id, confirm_nodename, and "
            "request.confirmation.phrase. Do not pass nodename as an execution "
            "selector; use confirm_nodename only for correlation. Requires "
            "Collector NodeExec or Manager privileges through MCP RBAC."
        ),
        tags={"nodes", "config", "pull", "exec:nodes"},
        annotations={
            "title": "Pull OpenSVC Node Configuration",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": False,
            "openWorldHint": False,
        },
    )
    async def pull_node_config(
        request: Annotated[
            PullNodeConfigRequest,
            Field(description="Node config pull selector and explicit confirmations."),
        ],
    ) -> PullNodeConfigResponse:
        """Enqueue a pull action for one OpenSVC Collector node."""
        response = await core_pull_node_config(
            node_id=request.node_id,
            nodename=None,
            confirm_node_id=request.confirm_node_id,
            confirm_nodename=request.confirm_nodename,
        )
        return PullNodeConfigResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="push_node_config",
        description=(
            "Enqueue a node-only OpenSVC configuration push action for one "
            "Collector node through PUT /actions with action=push. This queues "
            "the Collector node action handled as nodemgr push for the resolved "
            "node_id. It is not the future service-instance Push tool and does "
            "not take svc_id. This tool is node_id-only. If the user gives a "
            "nodename, first call get_node to resolve exactly one node and read "
            "its node_id and nodename. Do not ask for a runtime action "
            "confirmation before this resolution step. Then ask the user to "
            "repeat an exact phrase containing both resolved values, for "
            "example: PUSH config node <node_id> <nodename>. When the latest "
            "user message contains that phrase, call push_node_config with "
            "node_id, confirm_node_id, confirm_nodename, and "
            "request.confirmation.phrase. Do not pass nodename as an execution "
            "selector; use confirm_nodename only for correlation. Requires "
            "Collector NodeExec or Manager privileges through MCP RBAC."
        ),
        tags={"nodes", "config", "push", "exec:nodes"},
        annotations={
            "title": "Push OpenSVC Node Configuration",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": False,
            "openWorldHint": False,
        },
    )
    async def push_node_config(
        request: Annotated[
            PushNodeConfigRequest,
            Field(description="Node config push selector and explicit confirmations."),
        ],
    ) -> PushNodeConfigResponse:
        """Enqueue a push action for one OpenSVC Collector node."""
        response = await core_push_node_config(
            node_id=request.node_id,
            nodename=None,
            confirm_node_id=request.confirm_node_id,
            confirm_nodename=request.confirm_nodename,
        )
        return PushNodeConfigResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="update_node_compliance_modules",
        description=(
            "Enqueue a node compliance modules update for one OpenSVC Collector "
            "node through PUT /actions with action=updatecomp. This corresponds "
            "to the Collector UI action 'Update compliance modules' and asks the "
            "OpenSVC agent to download and install compliance module tarballs "
            "from node.repocomp or node.repo/compliance. This tool is "
            "node_id-only. If the user gives a nodename, first call get_node to "
            "resolve exactly one node and read its node_id and nodename. Do not "
            "ask for a runtime action confirmation before this resolution step. "
            "Then ask the user to repeat an exact phrase containing both resolved "
            "values, for example: UPDATE compliance modules node <node_id> "
            "<nodename>. When the latest user message contains that phrase, call "
            "update_node_compliance_modules with node_id, confirm_node_id, "
            "confirm_nodename, and request.confirmation.phrase. Do not pass "
            "nodename as an execution selector; use confirm_nodename only for "
            "correlation. Requires Collector NodeExec or Manager privileges "
            "through MCP RBAC."
        ),
        tags={"nodes", "compliance", "exec:nodes"},
        annotations={
            "title": "Update OpenSVC Node Compliance Modules",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": False,
            "openWorldHint": False,
        },
    )
    async def update_node_compliance_modules(
        request: Annotated[
            UpdateNodeComplianceModulesRequest,
            Field(
                description=(
                    "Node compliance module update selector and explicit confirmations."
                )
            ),
        ],
    ) -> UpdateNodeComplianceModulesResponse:
        """Enqueue an updatecomp action for one OpenSVC Collector node."""
        response = await core_update_node_compliance_modules(
            node_id=request.node_id,
            nodename=None,
            confirm_node_id=request.confirm_node_id,
            confirm_nodename=request.confirm_nodename,
        )
        return UpdateNodeComplianceModulesResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="update_node_opensvc_agent",
        description=(
            "Enqueue an OpenSVC agent package update for one Collector node "
            "through PUT /actions with action=updatepkg. This corresponds to the "
            "Collector UI action 'Update opensvc agent'. It upgrades only the "
            "OpenSVC agent package from node.repopkg or node.repo/packages using "
            "the node operating system package backend; it is not a general OS "
            "package update. This tool is node_id-only. If the user gives a "
            "nodename, first call get_node to resolve exactly one node and read "
            "its node_id and nodename. Do not ask for a runtime action "
            "confirmation before this resolution step. Then ask the user to "
            "repeat an exact phrase containing both resolved values, for "
            "example: UPDATE opensvc agent node <node_id> <nodename>. When the "
            "latest user message contains that phrase, call "
            "update_node_opensvc_agent with node_id, confirm_node_id, "
            "confirm_nodename, and request.confirmation.phrase. Do not pass "
            "nodename as an execution selector; use confirm_nodename only for "
            "correlation. Requires Collector NodeExec or Manager privileges "
            "through MCP RBAC."
        ),
        tags={"nodes", "agent", "exec:nodes"},
        annotations={
            "title": "Update OpenSVC Node Agent",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": False,
            "openWorldHint": False,
        },
    )
    async def update_node_opensvc_agent(
        request: Annotated[
            UpdateNodeOpensvcAgentRequest,
            Field(description="Node OpenSVC agent update selector and confirmations."),
        ],
    ) -> UpdateNodeOpensvcAgentResponse:
        """Enqueue an updatepkg action for one OpenSVC Collector node."""
        response = await core_update_node_opensvc_agent(
            node_id=request.node_id,
            nodename=None,
            confirm_node_id=request.confirm_node_id,
            confirm_nodename=request.confirm_nodename,
        )
        return UpdateNodeOpensvcAgentResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="scan_node_scsi",
        description=(
            "Enqueue a SCSI host rescan for one OpenSVC Collector node through "
            "PUT /actions with action=scanscsi. This corresponds to the Collector "
            "UI action 'Rescan scsi hosts'. It asks the OpenSVC agent to rescan "
            "the node operating system SCSI host buses for newly presented LUNs "
            "or disks; it is not a simple Collector disk inventory refresh. Run "
            "push_node_disks later if the user wants Collector disk inventory "
            "refreshed after discovery. This tool is node_id-only. If the user "
            "gives a nodename, first call get_node to resolve exactly one node "
            "and read its node_id and nodename. Do not ask for a runtime action "
            "confirmation before this resolution step. Then ask the user to "
            "repeat an exact phrase containing both resolved values, for "
            "example: SCAN scsi node <node_id> <nodename>. When the latest user "
            "message contains that phrase, call scan_node_scsi with node_id, "
            "confirm_node_id, confirm_nodename, and request.confirmation.phrase. "
            "Do not pass nodename as an execution selector; use confirm_nodename "
            "only for correlation. Requires Collector NodeExec or Manager "
            "privileges through MCP RBAC."
        ),
        tags={"nodes", "scsi", "disks", "exec:nodes"},
        annotations={
            "title": "Scan OpenSVC Node SCSI Hosts",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": False,
            "openWorldHint": False,
        },
    )
    async def scan_node_scsi(
        request: Annotated[
            ScanNodeScsiRequest,
            Field(description="Node SCSI scan selector and explicit confirmations."),
        ],
    ) -> ScanNodeScsiResponse:
        """Enqueue a scanscsi action for one OpenSVC Collector node."""
        response = await core_scan_node_scsi(
            node_id=request.node_id,
            nodename=None,
            confirm_node_id=request.confirm_node_id,
            confirm_nodename=request.confirm_nodename,
        )
        return ScanNodeScsiResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="reboot_node",
        description=(
            "Enqueue an immediate reboot action for one OpenSVC Collector node "
            "through PUT /actions with action=reboot. This corresponds to the "
            "Collector UI action 'Reboot'. It asks the OpenSVC agent to reboot "
            "the target node as soon as the queued action is executed; unlike "
            "schedule_node_reboot, it does not set a future reboot flag or wait "
            "for a configured reboot window. This tool is node_id-only. If the "
            "user gives a nodename, first call get_node to resolve exactly one "
            "node and read its node_id and nodename. Do not ask for a runtime "
            "action confirmation before this resolution step. Then ask the user "
            "to repeat an exact phrase containing both resolved values, for "
            "example: REBOOT node <node_id> <nodename>. When the latest user "
            "message contains that phrase, call reboot_node with node_id, "
            "confirm_node_id, confirm_nodename, and request.confirmation.phrase. "
            "Do not pass nodename as an execution selector; use confirm_nodename "
            "only for correlation. Requires Collector NodeExec or Manager "
            "privileges through MCP RBAC."
        ),
        tags={"nodes", "reboot", "exec:nodes"},
        annotations={
            "title": "Reboot OpenSVC Node",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": True,
            "openWorldHint": False,
        },
    )
    async def reboot_node(
        request: Annotated[
            RebootNodeRequest,
            Field(description="Node reboot selector and explicit confirmations."),
        ],
    ) -> RebootNodeResponse:
        """Enqueue a reboot action for one OpenSVC Collector node."""
        response = await core_reboot_node(
            node_id=request.node_id,
            nodename=None,
            confirm_node_id=request.confirm_node_id,
            confirm_nodename=request.confirm_nodename,
        )
        return RebootNodeResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="schedule_node_reboot",
        description=(
            "Enqueue a scheduled reboot flag action for one OpenSVC Collector "
            "node through PUT /actions with action=schedule_reboot. This "
            "corresponds to the Collector UI action 'Reboot schedule'. It asks "
            "the OpenSVC agent to mark the node for reboot at the next allowed "
            "reboot window configured on the node, usually by the [reboot] "
            "section in node.conf. This tool does not accept a date, time, or "
            "delay; it only sets the local OpenSVC reboot flag. This tool is "
            "node_id-only. If the user gives a nodename, first call get_node to "
            "resolve exactly one node and read its node_id and nodename. Do not "
            "ask for a runtime action confirmation before this resolution step. "
            "Then ask the user to repeat an exact phrase containing both "
            "resolved values, for example: SCHEDULE reboot node <node_id> "
            "<nodename>. When the latest user message contains that phrase, "
            "call schedule_node_reboot with node_id, confirm_node_id, "
            "confirm_nodename, and request.confirmation.phrase. Do not pass "
            "nodename as an execution selector; use confirm_nodename only for "
            "correlation. Requires Collector NodeExec or Manager privileges "
            "through MCP RBAC."
        ),
        tags={"nodes", "reboot", "exec:nodes"},
        annotations={
            "title": "Schedule OpenSVC Node Reboot",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": True,
            "openWorldHint": False,
        },
    )
    async def schedule_node_reboot(
        request: Annotated[
            ScheduleNodeRebootRequest,
            Field(description="Node reboot scheduling selector and confirmations."),
        ],
    ) -> ScheduleNodeRebootResponse:
        """Enqueue a schedule_reboot action for one OpenSVC Collector node."""
        response = await core_schedule_node_reboot(
            node_id=request.node_id,
            nodename=None,
            confirm_node_id=request.confirm_node_id,
            confirm_nodename=request.confirm_nodename,
        )
        return ScheduleNodeRebootResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="unschedule_node_reboot",
        description=(
            "Enqueue a scheduled reboot cancellation action for one OpenSVC "
            "Collector node through PUT /actions with action=unschedule_reboot. "
            "This corresponds to the Collector UI action 'Reboot unschedule'. "
            "It asks the OpenSVC agent to remove the local scheduled reboot "
            "flag from the node; it does not reboot or shut down the node. This "
            "tool is node_id-only. If the user gives a nodename, first call "
            "get_node to resolve exactly one node and read its node_id and "
            "nodename. Do not ask for a runtime action confirmation before this "
            "resolution step. Then ask the user to repeat an exact phrase "
            "containing both resolved values, for example: UNSCHEDULE reboot "
            "node <node_id> <nodename>. When the latest user message contains "
            "that phrase, call unschedule_node_reboot with node_id, "
            "confirm_node_id, confirm_nodename, and request.confirmation.phrase. "
            "Do not pass nodename as an execution selector; use "
            "confirm_nodename only for correlation. Requires Collector NodeExec "
            "or Manager privileges through MCP RBAC."
        ),
        tags={"nodes", "reboot", "exec:nodes"},
        annotations={
            "title": "Unschedule OpenSVC Node Reboot",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": False,
            "openWorldHint": False,
        },
    )
    async def unschedule_node_reboot(
        request: Annotated[
            UnscheduleNodeRebootRequest,
            Field(description="Node reboot unscheduling selector and confirmations."),
        ],
    ) -> UnscheduleNodeRebootResponse:
        """Enqueue an unschedule_reboot action for one OpenSVC Collector node."""
        response = await core_unschedule_node_reboot(
            node_id=request.node_id,
            nodename=None,
            confirm_node_id=request.confirm_node_id,
            confirm_nodename=request.confirm_nodename,
        )
        return UnscheduleNodeRebootResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="update_node_properties",
        description=(
            "Update Collector-writable properties on one existing OpenSVC "
            "Collector node. Destructive and node_id-only at the MCP boundary. "
            "If the user gives a nodename, first call get_node to resolve exactly "
            "one node and read its node_id and nodename. Do not ask for update "
            "confirmation before this resolution step. Then ask the user to "
            "repeat an exact phrase containing both resolved values and the "
            "property changes. When the latest user message contains that phrase, "
            "call update_node_properties with node_id, confirm_node_id, "
            "confirm_nodename, properties, and request.confirmation.phrase. Do "
            "not pass nodename as an execution selector; use confirm_nodename "
            "only for correlation. Collector still applies the update through "
            "POST /nodes/<resolved nodename>. Requires Collector NodeManager or "
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
            node_id=request.node_id,
            nodename=None,
            confirm_node_id=request.confirm_node_id,
            confirm_nodename=request.confirm_nodename,
            properties=request.properties,
        )
        return UpdateNodePropertiesResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="snooze_node_notifications",
        description=(
            "Snooze notifications on one OpenSVC Collector node through "
            "POST /nodes/<node_id>/snooze with duration. This tool is "
            "node_id-only. If the user gives a nodename, first call get_node to "
            "resolve exactly one node and read its node_id and nodename. Do not "
            "ask for confirmation before this resolution step. Then ask the user "
            "to repeat an exact phrase containing the resolved node_id, nodename, "
            "and duration. When the latest user message contains that phrase, "
            "call snooze_node_notifications with node_id, confirm_node_id, "
            "confirm_nodename, duration, and request.confirmation.phrase. Do not "
            "pass nodename as an execution selector; use confirm_nodename only "
            "for correlation. Requires Collector NodeManager or Manager "
            "privileges through MCP RBAC."
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
            nodename=None,
            duration=request.duration,
        )
        return SnoozeNodeNotificationsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="unsnooze_node_notifications",
        description=(
            "Unsnooze notifications on one OpenSVC Collector node through "
            "POST /nodes/<node_id>/snooze without duration. This tool is "
            "node_id-only. If the user gives a nodename, first call get_node to "
            "resolve exactly one node and read its node_id and nodename. Do not "
            "ask for confirmation before this resolution step. Then ask the user "
            "to repeat an exact phrase containing both resolved values. When the "
            "latest user message contains that phrase, call "
            "unsnooze_node_notifications with node_id, confirm_node_id, "
            "confirm_nodename, and request.confirmation.phrase. Do not pass "
            "nodename as an execution selector; use confirm_nodename only for "
            "correlation. Requires Collector NodeManager or Manager privileges "
            "through MCP RBAC."
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
            nodename=None,
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

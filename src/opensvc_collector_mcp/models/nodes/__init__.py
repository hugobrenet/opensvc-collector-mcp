"""Pydantic contracts for node tools."""

from ._common import (
    ConfirmedNodeIdRequest,
    NodeNameRequest,
    NodeRelationRequest,
    NodeSelector,
)

from .inventory import (
    NodeFilterRequest,
    CountNodesRequest,
    CountNodesResponse,
    CreateNodeRequest,
    CreateNodeResponse,
    ListNodesRequest,
    NodePropsResponse,
    NodeRowsResponse,
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
    ShutdownNodeRequest,
    ShutdownNodeResponse,
    ScheduleNodeRebootRequest,
    ScheduleNodeRebootResponse,
    UnscheduleNodeRebootRequest,
    UnscheduleNodeRebootResponse,
    RotateNodeRootPasswordRequest,
    RotateNodeRootPasswordResponse,
    WakeNodeOnLanRequest,
    WakeNodeOnLanResponse,
    SnoozeNodeNotificationsRequest,
    SnoozeNodeNotificationsResponse,
    UnsnoozeNodeNotificationsRequest,
    UnsnoozeNodeNotificationsResponse,
    UpdateNodePropertiesRequest,
    UpdateNodePropertiesResponse,
)

from .tags import (
    NodeTagsResponse,
)

from .location import (
    NodeLocation,
    NodeLocationResponse,
)

from .organization import (
    NodeOrganization,
    NodeOrganizationResponse,
)

from .hardware import (
    NodeHardwareIdentity,
    NodeCpuHardware,
    NodeMemoryHardware,
    NodePowerHardware,
    NodeHardwarePlacement,
    NodeHardwareResponse,
)

from .os import (
    NodeOperatingSystem,
    NodeOsRuntime,
    NodeOsResponse,
)

from .cluster import (
    NodeCluster,
    NodeClusterResponse,
)

from .network import (
    NodeNetworkEntry,
    NodeNetworkResponse,
)

from .compliance import (
    NodeComplianceEntry,
    NodeComplianceResponse,
)

from .checks import (
    NodeCheckEntry,
    NodeChecksResponse,
)

from .storage import (
    NodeDiskEntry,
    NodeDisksResponse,
)

from .services import (
    NodeServicesRequest,
    NodeService,
    NodeServicesResponse,
)

from .health import (
    NodeHealthIssue,
    NodeHealthResponse,
)

from .stats import (
    InventoryStatsRequest,
    InventoryStatsResponse,
)

__all__ = [
    'ConfirmedNodeIdRequest',
    'CountNodesRequest',
    'CountNodesResponse',
    'CreateNodeRequest',
    'CreateNodeResponse',
    'DeleteNodeRequest',
    'DeleteNodeResponse',
    'FreezeNodeRequest',
    'FreezeNodeResponse',
    'ThawNodeRequest',
    'ThawNodeResponse',
    'RunNodeChecksRequest',
    'RunNodeChecksResponse',
    'CollectNodeSysreportRequest',
    'CollectNodeSysreportResponse',
    'PushNodeAssetRequest',
    'PushNodeAssetResponse',
    'PushNodeDisksRequest',
    'PushNodeDisksResponse',
    'PushNodePackagesRequest',
    'PushNodePackagesResponse',
    'PushNodePatchesRequest',
    'PushNodePatchesResponse',
    'PushNodeStatsRequest',
    'PushNodeStatsResponse',
    'PullNodeConfigRequest',
    'PullNodeConfigResponse',
    'PushNodeConfigRequest',
    'PushNodeConfigResponse',
    'UpdateNodeComplianceModulesRequest',
    'UpdateNodeComplianceModulesResponse',
    'UpdateNodeOpensvcAgentRequest',
    'UpdateNodeOpensvcAgentResponse',
    'ScanNodeScsiRequest',
    'ScanNodeScsiResponse',
    'RebootNodeRequest',
    'RebootNodeResponse',
    'ShutdownNodeRequest',
    'ShutdownNodeResponse',
    'ScheduleNodeRebootRequest',
    'ScheduleNodeRebootResponse',
    'UnscheduleNodeRebootRequest',
    'UnscheduleNodeRebootResponse',
    'RotateNodeRootPasswordRequest',
    'RotateNodeRootPasswordResponse',
    'WakeNodeOnLanRequest',
    'WakeNodeOnLanResponse',
    'InventoryStatsRequest',
    'InventoryStatsResponse',
    'ListNodesRequest',
    'NodeCheckEntry',
    'NodeChecksResponse',
    'NodeCluster',
    'NodeClusterResponse',
    'NodeComplianceEntry',
    'NodeComplianceResponse',
    'NodeCpuHardware',
    'NodeDiskEntry',
    'NodeDisksResponse',
    'NodeFilterRequest',
    'NodeHardwareIdentity',
    'NodeHardwarePlacement',
    'NodeHardwareResponse',
    'NodeHealthIssue',
    'NodeHealthResponse',
    'NodeLocation',
    'NodeLocationResponse',
    'NodeMemoryHardware',
    'NodeNameRequest',
    'NodeRelationRequest',
    'NodeSelector',
    'NodeNetworkEntry',
    'NodeNetworkResponse',
    'NodeOperatingSystem',
    'NodeOrganization',
    'NodeOrganizationResponse',
    'NodeOsResponse',
    'NodeOsRuntime',
    'NodePowerHardware',
    'NodePropsResponse',
    'NodeRowsResponse',
    'NodeService',
    'NodeServicesRequest',
    'NodeServicesResponse',
    'NodeTagsResponse',
    'SnoozeNodeNotificationsRequest',
    'SnoozeNodeNotificationsResponse',
    'UnsnoozeNodeNotificationsRequest',
    'UnsnoozeNodeNotificationsResponse',
    'UpdateNodePropertiesRequest',
    'UpdateNodePropertiesResponse',
]

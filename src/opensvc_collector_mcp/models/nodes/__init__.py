"""Pydantic contracts for node tools."""

from ._common import (
    NodeNameRequest,
)

from .inventory import (
    NodeFilterRequest,
    SearchNodesRequest,
    CountNodesRequest,
    ListNodesRequest,
    NodePropsResponse,
    NodeRowsResponse,
    CountNodesResponse,
)

from .tags import (
    TagNameRequest,
    NodeTagsResponse,
    NodesByTagResponse,
    NodesWithoutTagResponse,
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
    'CountNodesRequest',
    'CountNodesResponse',
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
    'NodeServicesResponse',
    'NodeTagsResponse',
    'NodesByTagResponse',
    'NodesWithoutTagResponse',
    'SearchNodesRequest',
    'TagNameRequest',
]

from typing import Any

from pydantic import BaseModel, Field, ConfigDict, model_validator


class NodeFilterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filters: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Exact-match node property filters. Keys must be Collector node "
            "properties returned by list_node_props."
        ),
        examples=[{"status": "warn", "loc_city": "Paris, VINCENNES"}],
    )
    status: str | None = Field(default=None, description="Exact node status.")
    asset_env: str | None = Field(default=None, description="Exact asset environment.")
    node_env: str | None = Field(default=None, description="Exact node environment.")
    loc_city: str | None = Field(default=None, description="Exact node city.")
    loc_country: str | None = Field(default=None, description="Exact node country.")
    team_responsible: str | None = Field(default=None, description="Exact responsible team.")
    app: str | None = Field(default=None, description="Exact application name.")
    os_name: str | None = Field(default=None, description="Exact operating system name.")

    @model_validator(mode="after")
    def normalize_filters(self) -> "NodeFilterRequest":
        self.filters = {
            key.strip(): value.strip()
            for key, value in self.filters.items()
            if key.strip() and value.strip()
        }
        return self

    def merged_filters(self) -> dict[str, str]:
        merged = dict(self.filters)
        for field in (
            "status",
            "asset_env",
            "node_env",
            "loc_city",
            "loc_country",
            "team_responsible",
            "app",
            "os_name",
        ):
            value = getattr(self, field)
            if value is None:
                continue
            value = value.strip()
            if not value:
                continue
            existing = merged.get(field)
            if existing is not None and existing != value:
                raise ValueError(f"Conflicting filter values for {field!r}")
            merged[field] = value
        return merged


class SearchNodesRequest(NodeFilterRequest):
    nodename_contains: str | None = Field(
        default=None,
        description="Case-insensitive substring to find in nodenames.",
    )
    props: str | None = Field(
        default=None,
        description="Comma-separated node properties to return.",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of nodes to return.",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of matching nodes to skip.",
    )
    max_scan: int = Field(
        default=5000,
        ge=1,
        le=50000,
        description="Maximum candidate nodes to scan when using nodename_contains.",
    )


class CountNodesRequest(NodeFilterRequest):
    pass


class ListNodesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    props: str | None = Field(
        default=None,
        description="Comma-separated node properties to include in the response.",
    )


class NodeNameRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str = Field(
        min_length=1,
        description="Exact OpenSVC Collector nodename.",
        examples=["lab-paris-01"],
    )


class InventoryStatsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fields: str | None = Field(
        default=None,
        description=(
            "Comma-separated node properties to aggregate. Defaults to status, "
            "asset_env, node_env, loc_city, loc_country, app, and os_name."
        ),
    )
    page_size: int = Field(
        default=1000,
        ge=1,
        le=5000,
        description="Number of nodes fetched per Collector request.",
    )
    max_nodes: int = Field(
        default=200000,
        ge=1,
        le=500000,
        description="Maximum number of nodes to scan before returning partial stats.",
    )


class NodePropsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    count: int
    available_props: list[str]
    node_props: list[str]


class NodeRowsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[dict[str, Any]]


class NodeTagsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[dict[str, Any]]


class NodeLocation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    country: str | None = None
    city: str | None = None
    building: str | None = None
    room: str | None = None
    floor: str | None = None
    rack: str | None = None
    enclosure: str | None = None
    enclosure_slot: str | None = None
    address: str | None = None
    zip: str | None = None


class NodeLocationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str
    location: NodeLocation
    raw: dict[str, Any] = Field(default_factory=dict)


class NodeOrganization(BaseModel):
    model_config = ConfigDict(extra="forbid")

    responsible: str | None = None
    integration: str | None = None
    support: str | None = None
    app: str | None = None


class NodeOrganizationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str
    organization: NodeOrganization
    raw: dict[str, Any] = Field(default_factory=dict)


class NodeHardwareIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    serial: str | None = None
    bios_version: str | None = None


class NodeCpuHardware(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str | None = None
    vendor: str | None = None
    cores: int | None = None
    threads: int | None = None
    dies: int | None = None
    frequency: int | None = None


class NodeMemoryHardware(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bytes: int | None = None
    banks: int | None = None
    slots: int | None = None


class NodePowerHardware(BaseModel):
    model_config = ConfigDict(extra="forbid")

    supply_count: int | None = None
    cabinet1: str | None = None
    cabinet2: str | None = None
    breaker1: str | None = None
    breaker2: str | None = None
    protect: str | None = None
    protect_breaker: str | None = None


class NodeHardwarePlacement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enclosure: str | None = None
    enclosure_slot: str | None = None


class NodeHardwareResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str
    hardware: NodeHardwareIdentity
    cpu: NodeCpuHardware
    memory: NodeMemoryHardware
    power: NodePowerHardware
    placement: NodeHardwarePlacement
    raw: dict[str, Any] = Field(default_factory=dict)


class NodeOperatingSystem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    vendor: str | None = None
    release: str | None = None
    kernel: str | None = None
    arch: str | None = None
    concat: str | None = None


class NodeOsRuntime(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str | None = None
    service_pack: str | None = None
    timezone: str | None = None
    last_boot: str | None = None


class NodeOsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str
    os: NodeOperatingSystem
    runtime: NodeOsRuntime
    raw: dict[str, Any] = Field(default_factory=dict)


class NodeCluster(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str | None = None
    name: str | None = None


class NodeClusterResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str
    cluster: NodeCluster | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class NodeNetworkEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mac: str | None = None
    net_team_responsible: str | None = None
    intf: str | None = None
    addr: str | None = None
    prio: int | None = None
    net_gateway: str | None = None
    net_comment: str | None = None
    net_end: str | None = None
    net_netmask: str | None = None
    mask: str | None = None
    net_network: str | None = None
    addr_type: str | None = None
    net_broadcast: str | None = None
    net_pvid: int | None = None
    net_begin: str | None = None
    flag_deprecated: bool | None = None
    addr_updated: str | None = None
    net_id: int | None = None
    net_name: str | None = None


class NodeNetworkResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[NodeNetworkEntry]


class TagNameRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tag_name: str = Field(
        min_length=1,
        description="Exact OpenSVC Collector tag name.",
        examples=["test"],
    )


class NodesByTagResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tag_name: str
    tag_id: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[dict[str, Any]]


class NodesWithoutTagResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tag_name: str
    tag_id: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[dict[str, Any]]


class NodeComplianceEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    svc_id: str | None = None
    run_module: str | None = None
    run_date: str | None = None
    run_log: str | None = None
    node_id: str | None = None
    run_action: str | None = None
    rset_md5: str | None = None
    run_status: str | None = None
    id: int | None = None


class NodeComplianceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[NodeComplianceEntry]


class NodeService(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str | None = None
    svcname: str | None = None
    svc_status: str | None = None
    svc_env: str | None = None
    svc_app: str | None = None
    svc_topology: str | None = None
    mon_vmname: str | None = None
    mon_availstatus: str | None = None


class NodeServicesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[NodeService]


class CountNodesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    count: int | None
    filters: dict[str, str]


class NodeHealthIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    severity: str
    field: str
    message: str


class NodeHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    overall: str
    severity: str
    node: dict[str, Any]
    issues: list[NodeHealthIssue]
    signals: dict[str, Any]


class InventoryStatsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meta: dict[str, Any]
    stats: dict[str, dict[str, int]]

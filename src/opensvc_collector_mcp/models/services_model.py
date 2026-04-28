from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ServiceFilterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filters: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Exact-match service property filters. Keys must be Collector "
            "service properties returned by list_service_props."
        ),
        examples=[{"svc_env": "LAB", "svc_status": "up"}],
    )
    svcname: str | None = Field(default=None, description="Exact service name.")
    svc_app: str | None = Field(default=None, description="Exact service application.")
    svc_env: str | None = Field(
        default=None,
        description="Exact service environment. Use PRD for production services in this Collector.",
    )
    svc_status: str | None = Field(default=None, description="Exact service status.")
    svc_availstatus: str | None = Field(
        default=None,
        description="Exact service availability status.",
    )
    svc_topology: str | None = Field(default=None, description="Exact service topology.")
    svc_frozen: str | None = Field(default=None, description="Exact service frozen state.")

    @model_validator(mode="after")
    def normalize_filters(self) -> "ServiceFilterRequest":
        self.filters = {
            key.strip(): value.strip()
            for key, value in self.filters.items()
            if key.strip() and value.strip()
        }
        return self

    def merged_filters(self) -> dict[str, str]:
        merged = dict(self.filters)
        for field in (
            "svcname",
            "svc_app",
            "svc_env",
            "svc_status",
            "svc_availstatus",
            "svc_topology",
            "svc_frozen",
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


class ListServicesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    props: str | None = Field(
        default=None,
        description=(
            "Comma-separated service properties to include in the response. "
            "Defaults to a compact service inventory view."
        ),
    )


class SearchServicesRequest(ServiceFilterRequest):
    props: str | None = Field(
        default=None,
        description=(
            "Comma-separated service properties to include in the response. "
            "Defaults to a compact service inventory view."
        ),
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of services to return.",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of matching services to skip.",
    )


class CountServicesRequest(ServiceFilterRequest):
    pass


class FrozenServicesRequest(ServiceFilterRequest):
    min_frozen_days: int = Field(
        default=0,
        ge=0,
        le=3650,
        description="Only return services frozen for at least this many days.",
    )


class ServiceNameRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    svcname: str = Field(
        min_length=1,
        description="Exact OpenSVC Collector service name.",
        examples=["tst-lab-service"],
    )


class ServicePropsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    count: int
    available_props: list[str]
    service_props: list[str]


def _is_none(value: Any) -> bool:
    return value is None


class ServiceRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = Field(
        default=None,
        description="Collector internal row id.",
        exclude_if=_is_none,
    )
    svc_id: str | None = Field(
        default=None,
        description="Collector service uuid.",
        exclude_if=_is_none,
    )
    svcname: str | None = Field(
        default=None,
        description="OpenSVC service name.",
        exclude_if=_is_none,
    )
    svc_app: str | None = Field(
        default=None,
        description="Service application.",
        exclude_if=_is_none,
    )
    svc_env: str | None = Field(
        default=None,
        description="Service environment.",
        exclude_if=_is_none,
    )
    svc_status: str | None = Field(
        default=None,
        description="Service status.",
        exclude_if=_is_none,
    )
    svc_availstatus: str | None = Field(
        default=None,
        description="Service availability status.",
        exclude_if=_is_none,
    )
    svc_topology: str | None = Field(
        default=None,
        description="Service topology.",
        exclude_if=_is_none,
    )
    svc_nodes: str | None = Field(
        default=None,
        description="Service node list.",
        exclude_if=_is_none,
    )
    svc_drpnodes: str | None = Field(
        default=None,
        description="Service DRP node list.",
        exclude_if=_is_none,
    )
    svc_frozen: str | None = Field(
        default=None,
        description="Service frozen state.",
        exclude_if=_is_none,
    )
    svc_ha: int | None = Field(
        default=None,
        description="Service HA flag.",
        exclude_if=_is_none,
    )
    svc_placement: str | None = Field(
        default=None,
        description="Service placement state.",
        exclude_if=_is_none,
    )
    svc_provisioned: bool | str | None = Field(
        default=None,
        description="Service provisioned state as exposed by the Collector.",
        exclude_if=_is_none,
    )
    svc_notifications: bool | None = Field(
        default=None,
        description="Whether service notifications are enabled.",
        exclude_if=_is_none,
    )
    svc_created: str | None = Field(
        default=None,
        description="Service creation timestamp.",
        exclude_if=_is_none,
    )
    updated: str | None = Field(
        default=None,
        description="Service update timestamp.",
        exclude_if=_is_none,
    )
    svc_status_updated: str | None = Field(
        default=None,
        description="Service status update timestamp.",
        exclude_if=_is_none,
    )
    cluster_id: str | None = Field(
        default=None,
        description="Collector cluster uuid.",
        exclude_if=_is_none,
    )
    svc_config: str | None = Field(
        default=None,
        description="Full OpenSVC service configuration when returned by Collector.",
        exclude_if=_is_none,
    )


class ServiceRowsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ServiceRow]


class ServiceInstanceRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    svcname: str | None = Field(
        default=None,
        description="OpenSVC service name.",
        exclude_if=_is_none,
    )
    nodename: str | None = Field(
        default=None,
        description="Node hosting this service instance.",
        exclude_if=_is_none,
    )
    svc_app: str | None = Field(
        default=None,
        description="Service application.",
        exclude_if=_is_none,
    )
    svc_env: str | None = Field(
        default=None,
        description="Service environment.",
        exclude_if=_is_none,
    )
    svc_status: str | None = Field(
        default=None,
        description="Service status.",
        exclude_if=_is_none,
    )
    svc_availstatus: str | None = Field(
        default=None,
        description="Service availability status.",
        exclude_if=_is_none,
    )
    svc_topology: str | None = Field(
        default=None,
        description="Service topology.",
        exclude_if=_is_none,
    )
    mon_vmname: str | None = Field(
        default=None,
        description="Monitor VM or encapsulated instance name.",
        exclude_if=_is_none,
    )
    mon_availstatus: str | None = Field(
        default=None,
        description="Monitor availability status for this instance.",
        exclude_if=_is_none,
    )
    mon_frozen: bool | str | None = Field(
        default=None,
        description="Monitor frozen state for this instance.",
        exclude_if=_is_none,
    )
    mon_frozen_at: str | None = Field(
        default=None,
        description="Monitor frozen timestamp for this instance.",
        exclude_if=_is_none,
    )
    mon_encap_frozen_at: str | None = Field(
        default=None,
        description="Encapsulated monitor frozen timestamp for this instance.",
        exclude_if=_is_none,
    )


class ServiceInstancesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    svcname: str
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ServiceInstanceRow]


class ServiceResource(BaseModel):
    model_config = ConfigDict(extra="allow")

    rid: str = Field(description="OpenSVC resource identifier, for example disk#0.")
    resource_type: str = Field(
        description="Resource family derived from rid, for example disk, ip, fs, app, sync.",
    )
    nodename: str | None = Field(
        default=None,
        description="Node or encapsulated node this resource information belongs to.",
        exclude_if=_is_none,
    )
    driver: str | None = Field(
        default=None,
        description="OpenSVC resource driver.",
        exclude_if=_is_none,
    )
    name: str | None = Field(
        default=None,
        description="Resource name when exposed by Collector.",
        exclude_if=_is_none,
    )
    monitor: str | None = Field(
        default=None,
        description="Resource monitor setting.",
        exclude_if=_is_none,
    )
    optional: str | None = Field(
        default=None,
        description="Resource optional setting.",
        exclude_if=_is_none,
    )
    disabled: str | None = Field(
        default=None,
        description="Resource disabled setting.",
        exclude_if=_is_none,
    )
    shared: str | None = Field(
        default=None,
        description="Resource shared setting.",
        exclude_if=_is_none,
    )
    encap: str | None = Field(
        default=None,
        description="Resource encapsulation setting.",
        exclude_if=_is_none,
    )
    standby: str | None = Field(
        default=None,
        description="Resource standby setting.",
        exclude_if=_is_none,
    )
    tags: str | None = Field(
        default=None,
        description="Resource tags when exposed by Collector.",
        exclude_if=_is_none,
    )
    updated: str | None = Field(
        default=None,
        description="Most recent Collector update timestamp found for this resource.",
        exclude_if=_is_none,
    )
    properties: dict[str, Any] = Field(
        default_factory=dict,
        description="All resource key/value properties grouped from Collector resinfo rows.",
    )


class ServiceResourcesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    svcname: str
    meta: dict[str, Any] = Field(default_factory=dict)
    resources: list[ServiceResource]


class FrozenServiceInstance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str | None = Field(
        default=None,
        description="Node hosting the frozen service instance.",
        exclude_if=_is_none,
    )
    mon_vmname: str | None = Field(
        default=None,
        description="Monitor VM or encapsulated instance name.",
        exclude_if=_is_none,
    )
    mon_availstatus: str | None = Field(
        default=None,
        description="Monitor availability status for this frozen instance.",
        exclude_if=_is_none,
    )
    mon_frozen: bool | int | str | None = Field(
        default=None,
        description="Monitor frozen state returned by Collector.",
        exclude_if=_is_none,
    )
    mon_frozen_at: str | None = Field(
        default=None,
        description="Monitor frozen timestamp for this instance.",
        exclude_if=_is_none,
    )
    mon_encap_frozen_at: str | None = Field(
        default=None,
        description="Encapsulated monitor frozen timestamp for this instance.",
        exclude_if=_is_none,
    )


class FrozenService(BaseModel):
    model_config = ConfigDict(extra="forbid")

    svcname: str = Field(description="OpenSVC service name.")
    svc_env: str | None = Field(
        default=None,
        description="Service environment.",
        exclude_if=_is_none,
    )
    svc_app: str | None = Field(
        default=None,
        description="Service application.",
        exclude_if=_is_none,
    )
    svc_status: str | None = Field(
        default=None,
        description="Service status.",
        exclude_if=_is_none,
    )
    svc_availstatus: str | None = Field(
        default=None,
        description="Service availability status.",
        exclude_if=_is_none,
    )
    svc_frozen: bool | int | str | None = Field(
        default=None,
        description="Service frozen state returned by Collector.",
        exclude_if=_is_none,
    )
    svc_topology: str | None = Field(
        default=None,
        description="Service topology.",
        exclude_if=_is_none,
    )
    frozen_since: str | None = Field(
        default=None,
        description="Oldest frozen timestamp found across frozen instances.",
        exclude_if=_is_none,
    )
    frozen_days: int | None = Field(
        default=None,
        description="Whole days since frozen_since at query time.",
        exclude_if=_is_none,
    )
    frozen_instance_count: int = Field(
        description="Number of currently frozen monitor instances for this service."
    )
    nodes: list[str] = Field(description="Nodes hosting frozen instances.")
    instances: list[FrozenServiceInstance] = Field(
        description="Frozen monitor instances grouped under this service."
    )


class FrozenServicesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meta: dict[str, Any] = Field(
        default_factory=dict,
        description="Collector pagination metadata plus frozen service query summary.",
    )
    services: list[FrozenService] = Field(
        description="Services with currently frozen monitor instances."
    )


class ServiceHealthIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    severity: str = Field(description="Issue severity: warning, critical, or unknown.")
    field: str = Field(description="Service or instance field that triggered the issue.")
    message: str = Field(description="Human-readable health issue description.")


class ServiceHealthService(BaseModel):
    model_config = ConfigDict(extra="forbid")

    svcname: str | None = None
    svc_status: str | None = None
    svc_availstatus: str | None = None
    svc_frozen: str | None = None
    svc_topology: str | None = None
    svc_nodes: str | None = None
    svc_drpnodes: str | None = None
    svc_placement: str | None = None
    svc_ha: int | None = None
    updated: str | None = None
    svc_status_updated: str | None = None


class ServiceHealthSignals(BaseModel):
    model_config = ConfigDict(extra="forbid")

    instance_count: int
    nodes: list[str]
    active_nodes: list[str]
    inactive_nodes: list[str]
    availability_counts: dict[str, int]
    instances: list[ServiceInstanceRow]


class ServiceHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    overall: str = Field(description="Interpreted service health state.")
    severity: str = Field(description="Worst issue severity.")
    service: ServiceHealthService = Field(description="Service-level health signals.")
    issues: list[ServiceHealthIssue]
    signals: ServiceHealthSignals = Field(
        description="Instance-level health signals and raw instance rows.",
    )


class CountServicesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    count: int | None
    filters: dict[str, str]

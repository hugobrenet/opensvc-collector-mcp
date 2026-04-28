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


class ServiceConfigRequest(ServiceNameRequest):
    include_raw_config: bool = Field(
        default=True,
        description=(
            "Include the raw OpenSVC service configuration text. The text is "
            "bounded by raw_config_max_chars."
        ),
    )
    include_sections: bool = Field(
        default=True,
        description="Include parsed INI-like configuration sections and options.",
    )
    raw_config_max_chars: int = Field(
        default=20000,
        ge=0,
        le=100000,
        description="Maximum characters returned in the raw config field.",
    )


class ServiceActionsRequest(ServiceNameRequest):
    filters: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Exact-match service action filters. Keys can be Collector action "
            "properties such as action, status, ack, rid, subset, hostid, or node_id."
        ),
        examples=[{"status": "err"}],
    )
    action: str | None = Field(default=None, description="Exact action name filter.")
    status: str | None = Field(default=None, description="Exact action status filter.")
    ack: str | None = Field(default=None, description="Exact action ack state filter.")
    rid: str | None = Field(default=None, description="Exact resource id filter.")
    subset: str | None = Field(default=None, description="Exact action subset filter.")
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of service action rows to return.",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of matching action rows to skip when latest is false.",
    )
    latest: bool = Field(
        default=True,
        description="When true, return the most recent matching actions and ignore offset.",
    )
    latest_first: bool = Field(
        default=True,
        description="When true, return newest action rows first in the response.",
    )
    include_status_log: bool = Field(
        default=False,
        description="Include full Collector status_log values. Disabled by default because logs can be large.",
    )
    include_status_log_preview: bool = Field(
        default=True,
        description="Include a truncated status_log_preview when status_log is available.",
    )
    status_log_max_chars: int = Field(
        default=500,
        ge=0,
        le=5000,
        description="Maximum characters kept in status_log_preview.",
    )

    @model_validator(mode="after")
    def normalize_filters(self) -> "ServiceActionsRequest":
        self.filters = {
            key.strip(): value.strip()
            for key, value in self.filters.items()
            if key.strip() and value.strip()
        }
        return self

    def merged_filters(self) -> dict[str, str]:
        merged = dict(self.filters)
        for field in ("action", "status", "ack", "rid", "subset"):
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


class ServiceUnacknowledgedErrorsRequest(ServiceNameRequest):
    filters: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Exact-match service action filters for unacknowledged errors. "
            "Use action, rid, subset, hostid, or node_id. Do not pass status or ack; "
            "the endpoint is already scoped to err and unacknowledged actions."
        ),
        examples=[{"action": "start"}],
    )
    action: str | None = Field(default=None, description="Exact action name filter.")
    rid: str | None = Field(default=None, description="Exact resource id filter.")
    subset: str | None = Field(default=None, description="Exact action subset filter.")
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of unacknowledged error action rows to return.",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of matching error rows to skip when latest is false.",
    )
    latest: bool = Field(
        default=True,
        description="When true, return the most recent matching errors and ignore offset.",
    )
    latest_first: bool = Field(
        default=True,
        description="When true, return newest error rows first in the response.",
    )
    include_status_log: bool = Field(
        default=False,
        description="Include full Collector status_log values. Disabled by default because logs can be large.",
    )
    include_status_log_preview: bool = Field(
        default=True,
        description="Include a truncated status_log_preview when status_log is available.",
    )
    status_log_max_chars: int = Field(
        default=500,
        ge=0,
        le=5000,
        description="Maximum characters kept in status_log_preview.",
    )

    @model_validator(mode="after")
    def normalize_filters(self) -> "ServiceUnacknowledgedErrorsRequest":
        self.filters = {
            key.strip(): value.strip()
            for key, value in self.filters.items()
            if key.strip() and value.strip()
        }
        for field in self.filters:
            normalized = field.rsplit(".", 1)[-1]
            if normalized in {"status", "ack"}:
                raise ValueError(
                    "status and ack are implicit for unacknowledged error actions"
                )
        return self

    def merged_filters(self) -> dict[str, str]:
        merged = dict(self.filters)
        for field in ("action", "rid", "subset"):
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


class ServiceConfigSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="Configuration section name, for example DEFAULT or app#0.")
    options: dict[str, str] = Field(
        default_factory=dict,
        description="Configuration key/value options for this section.",
    )


class ServiceConfigResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    svcname: str
    meta: dict[str, Any] = Field(default_factory=dict)
    config_updated: str | None = Field(
        default=None,
        description="Collector timestamp for the service configuration update.",
        exclude_if=_is_none,
    )
    updated: str | None = Field(
        default=None,
        description="Collector service row update timestamp.",
        exclude_if=_is_none,
    )
    config: str | None = Field(
        default=None,
        description="Raw OpenSVC service configuration text, optionally truncated.",
        exclude_if=_is_none,
    )
    sections: list[ServiceConfigSection] = Field(
        default_factory=list,
        description="Parsed configuration sections and key/value options.",
    )


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


class ServiceActionRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    action: str | None = Field(
        default=None,
        description="OpenSVC action name, for example start, stop, provision, sync_all.",
        exclude_if=_is_none,
    )
    status: str | None = Field(
        default=None,
        description="Action execution status returned by Collector.",
        exclude_if=_is_none,
    )
    begin: str | None = Field(
        default=None,
        description="Action begin timestamp.",
        exclude_if=_is_none,
    )
    end: str | None = Field(
        default=None,
        description="Action end timestamp.",
        exclude_if=_is_none,
    )
    time: int | float | str | None = Field(
        default=None,
        description="Action duration when returned by Collector.",
        exclude_if=_is_none,
    )
    ack: bool | int | str | None = Field(
        default=None,
        description="Action acknowledgement state.",
        exclude_if=_is_none,
    )
    acked_by: str | None = Field(
        default=None,
        description="User who acknowledged the action error, when available.",
        exclude_if=_is_none,
    )
    acked_date: str | None = Field(
        default=None,
        description="Acknowledgement timestamp, when available.",
        exclude_if=_is_none,
    )
    acked_comment: str | None = Field(
        default=None,
        description="Acknowledgement comment, when available.",
        exclude_if=_is_none,
    )
    rid: str | None = Field(
        default=None,
        description="Resource id targeted by the action, when available.",
        exclude_if=_is_none,
    )
    subset: str | None = Field(
        default=None,
        description="Action subset, when available.",
        exclude_if=_is_none,
    )
    hostid: str | None = Field(
        default=None,
        description="Host id returned by Collector, when available.",
        exclude_if=_is_none,
    )
    node_id: str | None = Field(
        default=None,
        description="Collector node uuid returned for the action, when available.",
        exclude_if=_is_none,
    )
    status_log_preview: str | None = Field(
        default=None,
        description="Truncated status log preview when requested.",
        exclude_if=_is_none,
    )
    status_log: str | None = Field(
        default=None,
        description="Full status log, only included when include_status_log is true.",
        exclude_if=_is_none,
    )


class ServiceActionsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    svcname: str
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ServiceActionRow]


class ServiceUnacknowledgedErrorsResponse(ServiceActionsResponse):
    pass


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

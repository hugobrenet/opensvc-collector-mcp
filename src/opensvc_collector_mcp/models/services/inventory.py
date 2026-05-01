from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ._common import ServiceNameRequest, ServiceRelationCollectionRequest, _is_none


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
    svc_topology: str | None = Field(
        default=None, description="Exact service topology."
    )
    svc_frozen: str | None = Field(
        default=None, description="Exact service frozen state."
    )

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


class ServiceCollectionRequest(ServiceFilterRequest):
    props: str | None = Field(
        default=None,
        description=(
            "Comma-separated service properties to include in the response. "
            "Defaults to a compact service inventory view."
        ),
    )
    orderby: str | None = Field(
        default=None,
        description="Collector orderby expression, for example svcname or ~updated.",
    )
    search: str | None = Field(
        default=None,
        description="Collector full-text search expression when supported by /services.",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=1000,
        description="Maximum number of services to return.",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of matching services to skip.",
    )


class ListServicesRequest(ServiceCollectionRequest):
    pass


class SearchServicesRequest(ServiceCollectionRequest):
    pass


class CountServicesRequest(ServiceFilterRequest):
    pass


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


class ServiceInstancesRequest(ServiceRelationCollectionRequest):
    pass


class ServiceNodesRequest(ServiceRelationCollectionRequest):
    pass


class ServicePropsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    count: int
    available_props: list[str]
    service_props: list[str]


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

    name: str = Field(
        description="Configuration section name, for example DEFAULT or app#0."
    )
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


class ServiceNodeRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = Field(
        default=None,
        description="Collector service monitor row id.",
        exclude_if=_is_none,
    )
    svc_id: str | None = Field(
        default=None,
        description="Collector service uuid.",
        exclude_if=_is_none,
    )
    nodename: str | None = Field(
        default=None,
        description="Node where the service is known by Collector.",
        exclude_if=_is_none,
    )
    node_id: str | None = Field(
        default=None,
        description="Collector node uuid.",
        exclude_if=_is_none,
    )
    mon_vmname: str | None = Field(
        default=None,
        description="Monitor VM or encapsulated instance name.",
        exclude_if=_is_none,
    )
    mon_overallstatus: str | None = Field(
        default=None,
        description="Overall monitor status for this service on this node.",
        exclude_if=_is_none,
    )
    mon_availstatus: str | None = Field(
        default=None,
        description="Availability monitor status for this service on this node.",
        exclude_if=_is_none,
    )
    mon_frozen: int | bool | str | None = Field(
        default=None,
        description="Monitor frozen state for this service on this node.",
        exclude_if=_is_none,
    )
    mon_frozen_at: str | None = Field(
        default=None,
        description="Monitor frozen timestamp for this service on this node.",
        exclude_if=_is_none,
    )
    mon_encap_frozen_at: str | None = Field(
        default=None,
        description="Encapsulated monitor frozen timestamp for this service on this node.",
        exclude_if=_is_none,
    )
    mon_updated: str | None = Field(
        default=None,
        description="Monitor update timestamp for this service on this node.",
        exclude_if=_is_none,
    )
    mon_changed: str | None = Field(
        default=None,
        description="Monitor status change timestamp for this service on this node.",
        exclude_if=_is_none,
    )


class ServiceNodesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    svcname: str
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ServiceNodeRow]


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


class CountServicesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    count: int | None
    filters: dict[str, str]

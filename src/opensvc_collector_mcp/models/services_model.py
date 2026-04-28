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


class ServiceTagSearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tag_name: str = Field(
        min_length=1,
        description="Exact OpenSVC Collector tag name.",
        examples=["LAB-TAG"],
    )
    props: str | None = Field(
        default=None,
        description=(
            "Comma-separated service properties to return. svcname is always "
            "included because it is required to identify services."
        ),
    )
    page_size: int = Field(
        default=1000,
        ge=1,
        le=5000,
        description="Internal Collector page size used for paged reads.",
    )
    max_services: int = Field(
        default=200000,
        ge=1,
        le=500000,
        description="Maximum number of services the tool may scan or return.",
    )


class ServiceNodesRequest(ServiceNameRequest):
    props: str | None = Field(
        default=None,
        description=(
            "Comma-separated service node properties to return. Defaults to a "
            "compact per-node monitor view with nodename and key statuses."
        ),
    )
    page_size: int = Field(
        default=1000,
        ge=1,
        le=5000,
        description="Internal Collector page size used to retrieve all service nodes.",
    )
    max_nodes: int = Field(
        default=10000,
        ge=1,
        le=100000,
        description="Maximum number of service node rows the tool may return.",
    )


class ServiceHbasRequest(ServiceNameRequest):
    props: str | None = Field(
        default=None,
        description=(
            "Comma-separated service HBA properties to return. Defaults to a "
            "compact flat HBA view with node, HBA id, HBA type, and update time."
        ),
    )
    page_size: int = Field(
        default=1000,
        ge=1,
        le=5000,
        description="Internal Collector page size used to retrieve all service HBAs.",
    )
    max_hbas: int = Field(
        default=10000,
        ge=1,
        le=100000,
        description="Maximum number of service HBA rows the tool may return.",
    )


class ServiceTargetsRequest(ServiceNameRequest):
    filters: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Exact-match service target filters. Keys can be hba_id, node_id, "
            "tgt_id, array_name, or their stor_zone.<field> or stor_array.<field> form."
        ),
        examples=[{"hba_id": "LAB-HBA-01"}],
    )
    hba_id: str | None = Field(default=None, description="Exact HBA identifier filter.")
    node_id: str | None = Field(default=None, description="Exact Collector node uuid filter.")
    tgt_id: str | None = Field(default=None, description="Exact storage target identifier filter.")
    array_name: str | None = Field(default=None, description="Exact storage array name filter.")
    props: str | None = Field(
        default=None,
        description=(
            "Comma-separated service target properties to return. Defaults to a "
            "compact flat target view with node, HBA, target, and array fields."
        ),
    )
    page_size: int = Field(
        default=1000,
        ge=1,
        le=5000,
        description="Internal Collector page size used to retrieve all service targets.",
    )
    max_targets: int = Field(
        default=10000,
        ge=1,
        le=100000,
        description="Maximum number of service target rows the tool may return.",
    )

    @model_validator(mode="after")
    def normalize_filters(self) -> "ServiceTargetsRequest":
        self.filters = {
            key.strip(): value.strip()
            for key, value in self.filters.items()
            if key.strip() and value.strip()
        }
        return self

    def merged_filters(self) -> dict[str, str]:
        merged = dict(self.filters)
        for field in ("hba_id", "node_id", "tgt_id", "array_name"):
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


class ServiceDisksRequest(ServiceNameRequest):
    props: str | None = Field(
        default=None,
        description=(
            "Comma-separated service disk properties to return. Defaults to a "
            "compact flat disk view with node, size, local/SAN, diskinfo, and "
            "storage array fields."
        ),
    )
    page_size: int = Field(
        default=1000,
        ge=1,
        le=5000,
        description="Internal Collector page size used to retrieve all service disks.",
    )
    max_disks: int = Field(
        default=10000,
        ge=1,
        le=100000,
        description="Maximum number of service disk rows the tool may return.",
    )


class ServiceTagsRequest(ServiceNameRequest):
    filters: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Exact-match service tag filters. Keys can be tag_name, tag_id, "
            "tag_exclude, tag_data, or their tags.<field> form."
        ),
        examples=[{"tag_name": "LAB-TAG"}],
    )
    tag_name: str | None = Field(default=None, description="Exact tag name filter.")
    tag_id: str | None = Field(default=None, description="Exact Collector tag id filter.")
    tag_exclude: str | None = Field(default=None, description="Exact tag exclude filter.")
    props: str | None = Field(
        default=None,
        description=(
            "Comma-separated tag properties to return. Defaults to a compact "
            "service tag view."
        ),
    )
    page_size: int = Field(
        default=1000,
        ge=1,
        le=5000,
        description="Internal Collector page size used to retrieve all matching tags.",
    )
    max_tags: int = Field(
        default=10000,
        ge=1,
        le=100000,
        description="Maximum number of matching tags the tool may return.",
    )

    @model_validator(mode="after")
    def normalize_filters(self) -> "ServiceTagsRequest":
        self.filters = {
            key.strip(): value.strip()
            for key, value in self.filters.items()
            if key.strip() and value.strip()
        }
        return self

    def merged_filters(self) -> dict[str, str]:
        merged = dict(self.filters)
        for field in ("tag_name", "tag_id", "tag_exclude"):
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


class ServiceChecksRequest(ServiceNameRequest):
    filters: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Exact-match service check filters. Keys can be Collector check "
            "fields such as chk_type, chk_err, chk_instance, node_id, or their "
            "checks_live.<field> form."
        ),
        examples=[{"chk_type": "fs_u", "chk_err": "1"}],
    )
    chk_type: str | None = Field(default=None, description="Exact check type filter.")
    chk_err: int | None = Field(
        default=None,
        ge=0,
        description="Exact check error flag filter, usually 0 or 1.",
    )
    node_id: str | None = Field(default=None, description="Exact Collector node uuid filter.")
    chk_instance: str | None = Field(default=None, description="Exact check instance filter.")
    props: str | None = Field(
        default=None,
        description=(
            "Comma-separated check properties to return. Defaults to a compact "
            "service check view."
        ),
    )
    page_size: int = Field(
        default=1000,
        ge=1,
        le=5000,
        description="Internal Collector page size used to retrieve all matching checks.",
    )
    max_checks: int = Field(
        default=10000,
        ge=1,
        le=100000,
        description="Maximum number of matching checks the tool may return.",
    )

    @model_validator(mode="after")
    def normalize_filters(self) -> "ServiceChecksRequest":
        self.filters = {
            key.strip(): value.strip()
            for key, value in self.filters.items()
            if key.strip() and value.strip()
        }
        return self

    def merged_filters(self) -> dict[str, str]:
        merged = dict(self.filters)
        for field in ("chk_type", "node_id", "chk_instance"):
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
        if self.chk_err is not None:
            value = str(self.chk_err)
            existing = merged.get("chk_err")
            if existing is not None and existing != value:
                raise ValueError("Conflicting filter values for 'chk_err'")
            merged["chk_err"] = value
        return merged


class ServiceAlertsRequest(ServiceNameRequest):
    filters: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Exact-match service alert filters. Keys can be alert or Collector "
            "dashboard fields such as dash_type, dash_severity, node_id, or "
            "their dashboard.<field> form."
        ),
        examples=[{"dash_type": "action errors"}],
    )
    dash_type: str | None = Field(default=None, description="Exact alert type filter.")
    dash_severity: int | None = Field(
        default=None,
        ge=0,
        description="Exact dashboard alert severity filter.",
    )
    node_id: str | None = Field(default=None, description="Exact Collector node uuid filter.")
    props: str | None = Field(
        default=None,
        description=(
            "Comma-separated alert properties to return. Defaults to a compact "
            "alert view without large dashboard payload fields."
        ),
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of service alert rows to return.",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of matching service alert rows to skip.",
    )

    @model_validator(mode="after")
    def normalize_filters(self) -> "ServiceAlertsRequest":
        self.filters = {
            key.strip(): value.strip()
            for key, value in self.filters.items()
            if key.strip() and value.strip()
        }
        return self

    def merged_filters(self) -> dict[str, str]:
        merged = dict(self.filters)
        for field in ("dash_type", "node_id"):
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
        if self.dash_severity is not None:
            value = str(self.dash_severity)
            existing = merged.get("dash_severity")
            if existing is not None and existing != value:
                raise ValueError("Conflicting filter values for 'dash_severity'")
            merged["dash_severity"] = value
        return merged


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


class ServiceStatusHistoryRequest(ServiceNameRequest):
    filters: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Exact-match service status history filters. Keys can be "
            "svc_availstatus, svc_begin, svc_end, id, or their v_services_log.<field> form."
        ),
        examples=[{"svc_availstatus": "down"}],
    )
    svc_availstatus: str | None = Field(
        default=None,
        description="Exact service availability status filter, for example up, warn, or down.",
    )
    props: str | None = Field(
        default=None,
        description=(
            "Comma-separated status history properties to return. Defaults to "
            "svc_id, svc_begin, svc_end, svc_availstatus, and id."
        ),
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of status history rows to return.",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of sorted history rows to skip when latest is false.",
    )
    latest: bool = Field(
        default=True,
        description="When true, return the newest matching status rows and ignore offset.",
    )
    latest_first: bool = Field(
        default=True,
        description="When true, sort status history newest first.",
    )
    page_size: int = Field(
        default=1000,
        ge=1,
        le=5000,
        description="Internal Collector page size used to retrieve matching status history.",
    )
    max_history: int = Field(
        default=10000,
        ge=1,
        le=100000,
        description="Maximum number of status history rows the tool may scan.",
    )

    @model_validator(mode="after")
    def normalize_filters(self) -> "ServiceStatusHistoryRequest":
        self.filters = {
            key.strip(): value.strip()
            for key, value in self.filters.items()
            if key.strip() and value.strip()
        }
        return self

    def merged_filters(self) -> dict[str, str]:
        merged = dict(self.filters)
        if self.svc_availstatus is not None:
            value = self.svc_availstatus.strip()
            if value:
                existing = merged.get("svc_availstatus")
                if existing is not None and existing != value:
                    raise ValueError("Conflicting filter values for 'svc_availstatus'")
                merged["svc_availstatus"] = value
        return merged


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


class ServiceStatusHistoryRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | str | None = Field(
        default=None,
        description="Collector service status history row id.",
        exclude_if=_is_none,
    )
    svc_id: str | None = Field(
        default=None,
        description="Collector service uuid.",
        exclude_if=_is_none,
    )
    svc_begin: str | None = Field(
        default=None,
        description="Timestamp when this availability status period started.",
        exclude_if=_is_none,
    )
    svc_end: str | None = Field(
        default=None,
        description="Timestamp when this availability status period ended.",
        exclude_if=_is_none,
    )
    svc_availstatus: str | None = Field(
        default=None,
        description="Service availability status for this history period.",
        exclude_if=_is_none,
    )


class ServiceStatusHistoryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    svcname: str
    svc_id: str | None = Field(default=None, exclude_if=_is_none)
    service: ServiceRow = Field(
        default_factory=ServiceRow,
        description="Current service state used as context for the history.",
    )
    current_status_since: str | None = Field(
        default=None,
        description="Best matching start timestamp for the current service availability status.",
        exclude_if=_is_none,
    )
    current_history: ServiceStatusHistoryRow | None = Field(
        default=None,
        description="History row matching the current service availability status.",
        exclude_if=_is_none,
    )
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ServiceStatusHistoryRow]


class ServiceTagRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    tag_name: str | None = Field(
        default=None,
        description="Service tag name.",
        exclude_if=_is_none,
    )
    tag_id: str | None = Field(
        default=None,
        description="Collector tag id.",
        exclude_if=_is_none,
    )
    tag_data: str | None = Field(
        default=None,
        description="Tag data payload when returned by Collector.",
        exclude_if=_is_none,
    )
    tag_exclude: str | None = Field(
        default=None,
        description="Tag exclusion flag or expression when returned by Collector.",
        exclude_if=_is_none,
    )
    tag_created: str | None = Field(
        default=None,
        description="Tag creation timestamp.",
        exclude_if=_is_none,
    )


class ServiceTagsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    svcname: str
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ServiceTagRow]


class ServicesByTagResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tag_name: str
    tag_id: str | None = Field(default=None, exclude_if=_is_none)
    tag: ServiceTagRow | None = Field(default=None, exclude_if=_is_none)
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ServiceRow]


class ServicesWithoutTagResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tag_name: str
    tag_id: str | None = Field(default=None, exclude_if=_is_none)
    tag: ServiceTagRow | None = Field(default=None, exclude_if=_is_none)
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ServiceRow]


class ServiceCheckRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = Field(default=None, description="Collector check id.", exclude_if=_is_none)
    node_id: str | None = Field(default=None, description="Collector node uuid.", exclude_if=_is_none)
    chk_type: str | None = Field(default=None, description="Check type.", exclude_if=_is_none)
    chk_instance: str | None = Field(default=None, description="Check instance.", exclude_if=_is_none)
    chk_value: int | float | str | None = Field(default=None, description="Current check value.", exclude_if=_is_none)
    chk_err: int | str | None = Field(default=None, description="Check error flag or state.", exclude_if=_is_none)
    chk_low: int | float | str | None = Field(default=None, description="Low threshold.", exclude_if=_is_none)
    chk_high: int | float | str | None = Field(default=None, description="High threshold.", exclude_if=_is_none)
    chk_threshold_provider: str | None = Field(default=None, description="Threshold provider.", exclude_if=_is_none)
    chk_created: str | None = Field(default=None, description="Check creation timestamp.", exclude_if=_is_none)
    chk_updated: str | None = Field(default=None, description="Check update timestamp.", exclude_if=_is_none)


class ServiceChecksResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    svcname: str
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ServiceCheckRow]


class ServiceAlertRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = Field(
        default=None,
        description="Collector dashboard alert id.",
        exclude_if=_is_none,
    )
    alert: str | None = Field(
        default=None,
        description="Human-readable alert message.",
        exclude_if=_is_none,
    )
    dash_type: str | None = Field(
        default=None,
        description="Dashboard alert type.",
        exclude_if=_is_none,
    )
    dash_severity: int | str | None = Field(
        default=None,
        description="Dashboard alert severity.",
        exclude_if=_is_none,
    )
    dash_created: str | None = Field(
        default=None,
        description="Alert creation timestamp.",
        exclude_if=_is_none,
    )
    dash_updated: str | None = Field(
        default=None,
        description="Alert update timestamp.",
        exclude_if=_is_none,
    )
    node_id: str | None = Field(
        default=None,
        description="Collector node uuid when the alert is node-specific.",
        exclude_if=_is_none,
    )
    dash_env: str | None = Field(
        default=None,
        description="Dashboard alert environment when returned.",
        exclude_if=_is_none,
    )
    dash_instance: str | None = Field(
        default=None,
        description="Dashboard alert instance when returned.",
        exclude_if=_is_none,
    )


class ServiceAlertsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    svcname: str
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ServiceAlertRow]


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


class ServiceHbaRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = Field(
        default=None,
        description="Collector HBA row id.",
        exclude_if=_is_none,
    )
    nodename: str | None = Field(
        default=None,
        description="Node associated with this HBA row.",
        exclude_if=_is_none,
    )
    node_id: str | None = Field(
        default=None,
        description="Collector node uuid.",
        exclude_if=_is_none,
    )
    hba_id: str | None = Field(
        default=None,
        description="HBA identifier, such as a Fibre Channel WWPN or iSCSI IQN.",
        exclude_if=_is_none,
    )
    hba_type: str | None = Field(
        default=None,
        description="HBA type, for example fc or iscsi.",
        exclude_if=_is_none,
    )
    updated: str | None = Field(
        default=None,
        description="Collector HBA update timestamp.",
        exclude_if=_is_none,
    )


class ServiceHbasResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    svcname: str
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ServiceHbaRow]


class ServiceTargetRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = Field(
        default=None,
        description="Collector storage zone row id.",
        exclude_if=_is_none,
    )
    nodename: str | None = Field(
        default=None,
        description="Node associated with this target row.",
        exclude_if=_is_none,
    )
    node_id: str | None = Field(
        default=None,
        description="Collector node uuid.",
        exclude_if=_is_none,
    )
    hba_id: str | None = Field(
        default=None,
        description="HBA identifier used to reach this target.",
        exclude_if=_is_none,
    )
    tgt_id: str | None = Field(
        default=None,
        description="Storage target identifier.",
        exclude_if=_is_none,
    )
    array_id: int | str | None = Field(
        default=None,
        description="Collector storage array row id.",
        exclude_if=_is_none,
    )
    array_name: str | None = Field(
        default=None,
        description="Storage array name.",
        exclude_if=_is_none,
    )
    array_model: str | None = Field(
        default=None,
        description="Storage array model.",
        exclude_if=_is_none,
    )
    array_firmware: str | None = Field(
        default=None,
        description="Storage array firmware.",
        exclude_if=_is_none,
    )
    array_comment: str | None = Field(
        default=None,
        description="Storage array comment.",
        exclude_if=_is_none,
    )
    updated: str | None = Field(
        default=None,
        description="Collector target update timestamp.",
        exclude_if=_is_none,
    )


class ServiceTargetsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    svcname: str
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ServiceTargetRow]


class ServiceDiskRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = Field(
        default=None,
        description="Collector service disk row id.",
        exclude_if=_is_none,
    )
    svc_id: str | None = Field(
        default=None,
        description="Collector service uuid.",
        exclude_if=_is_none,
    )
    nodename: str | None = Field(
        default=None,
        description="Node associated with this service disk row.",
        exclude_if=_is_none,
    )
    node_id: str | None = Field(
        default=None,
        description="Collector node uuid.",
        exclude_if=_is_none,
    )
    disk_id: str | None = Field(
        default=None,
        description="Collector disk identifier.",
        exclude_if=_is_none,
    )
    disk_name: str | None = Field(
        default=None,
        description="Human-readable disk name when known by Collector.",
        exclude_if=_is_none,
    )
    disk_size: int | float | str | None = Field(
        default=None,
        description="Disk size as exposed by Collector.",
        exclude_if=_is_none,
    )
    disk_used: int | float | str | None = Field(
        default=None,
        description="Disk used size as exposed by Collector.",
        exclude_if=_is_none,
    )
    disk_local: bool | str | None = Field(
        default=None,
        description="Whether Collector marks this disk as local to the node.",
        exclude_if=_is_none,
    )
    disk_vendor: str | None = Field(
        default=None,
        description="Disk vendor.",
        exclude_if=_is_none,
    )
    disk_model: str | None = Field(
        default=None,
        description="Disk model.",
        exclude_if=_is_none,
    )
    disk_dg: str | None = Field(
        default=None,
        description="Disk device group or storage identifier when returned.",
        exclude_if=_is_none,
    )
    disk_region: str | None = Field(
        default=None,
        description="Disk region or allocation region when returned.",
        exclude_if=_is_none,
    )
    disk_devid: str | None = Field(
        default=None,
        description="Device identifier from diskinfo.",
        exclude_if=_is_none,
    )
    disk_alloc: int | float | str | None = Field(
        default=None,
        description="Allocated disk size or allocation metric from diskinfo.",
        exclude_if=_is_none,
    )
    disk_raid: str | None = Field(
        default=None,
        description="RAID or storage layout information.",
        exclude_if=_is_none,
    )
    disk_group: str | None = Field(
        default=None,
        description="Storage disk group.",
        exclude_if=_is_none,
    )
    disk_arrayid: str | None = Field(
        default=None,
        description="Storage array identifier associated with this disk.",
        exclude_if=_is_none,
    )
    array_name: str | None = Field(
        default=None,
        description="Storage array name.",
        exclude_if=_is_none,
    )
    array_model: str | None = Field(
        default=None,
        description="Storage array model.",
        exclude_if=_is_none,
    )
    disk_updated: str | None = Field(
        default=None,
        description="Collector disk update timestamp.",
        exclude_if=_is_none,
    )


class ServiceDisksResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    svcname: str
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ServiceDiskRow]


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

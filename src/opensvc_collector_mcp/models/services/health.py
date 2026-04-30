from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ._common import ServiceNameRequest, _is_none
from .inventory import ServiceFilterRequest, ServiceInstanceRow, ServiceRow


class FrozenServicesRequest(ServiceFilterRequest):
    min_frozen_days: int = Field(
        default=0,
        ge=0,
        le=3650,
        description="Only return services frozen for at least this many days.",
    )


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


class ServiceInstanceStatusHistoryRequest(ServiceNameRequest):
    filters: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Exact-match service instance status history filters. Keys can be "
            "node_id, nodename, mon_availstatus, mon_overallstatus, or their "
            "v_svcmon_log.<field> form."
        ),
        examples=[{"mon_availstatus": "down"}],
    )
    node_id: str | None = Field(default=None, description="Exact Collector node uuid filter.")
    nodename: str | None = Field(default=None, description="Exact node name filter.")
    mon_availstatus: str | None = Field(
        default=None,
        description="Exact monitor availability status filter, for example up or down.",
    )
    mon_overallstatus: str | None = Field(
        default=None,
        description="Exact monitor overall status filter, for example up or warn.",
    )
    props: str | None = Field(
        default=None,
        description=(
            "Comma-separated instance status history properties to return. "
            "Defaults to service, node, monitor status, and period fields."
        ),
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of instance status history rows to return.",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of matching history rows to skip when latest is false.",
    )
    latest: bool = Field(
        default=True,
        description="When true, return the newest matching instance status rows.",
    )
    latest_first: bool = Field(
        default=True,
        description="When true, sort instance status history newest first.",
    )
    page_size: int = Field(
        default=1000,
        ge=1,
        le=5000,
        description="Internal Collector page size used to retrieve matching rows.",
    )
    max_history: int = Field(
        default=1000,
        ge=1,
        le=100000,
        description="Maximum number of instance status history rows the tool may scan.",
    )

    @model_validator(mode="after")
    def normalize_filters(self) -> "ServiceInstanceStatusHistoryRequest":
        self.filters = {
            key.strip(): value.strip()
            for key, value in self.filters.items()
            if key.strip() and value.strip()
        }
        return self

    def merged_filters(self) -> dict[str, str]:
        merged = dict(self.filters)
        for field in ("node_id", "nodename", "mon_availstatus", "mon_overallstatus"):
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


class ServiceInstanceStatusHistoryRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | str | None = Field(
        default=None,
        description="Collector service instance status history row id.",
        exclude_if=_is_none,
    )
    svcname: str | None = Field(
        default=None,
        description="OpenSVC service name returned through the Collector join.",
        exclude_if=_is_none,
    )
    svc_id: str | None = Field(
        default=None,
        description="Collector service uuid.",
        exclude_if=_is_none,
    )
    nodename: str | None = Field(
        default=None,
        description="Node name returned through the Collector join.",
        exclude_if=_is_none,
    )
    node_id: str | None = Field(
        default=None,
        description="Collector node uuid.",
        exclude_if=_is_none,
    )
    mon_begin: str | None = Field(
        default=None,
        description="Timestamp when this monitor status period started.",
        exclude_if=_is_none,
    )
    mon_end: str | None = Field(
        default=None,
        description="Timestamp when this monitor status period ended.",
        exclude_if=_is_none,
    )
    mon_availstatus: str | None = Field(
        default=None,
        description="Instance monitor availability status for this history period.",
        exclude_if=_is_none,
    )
    mon_overallstatus: str | None = Field(
        default=None,
        description="Instance monitor overall status for this history period.",
        exclude_if=_is_none,
    )
    mon_appstatus: str | None = Field(default=None, exclude_if=_is_none)
    mon_containerstatus: str | None = Field(default=None, exclude_if=_is_none)
    mon_diskstatus: str | None = Field(default=None, exclude_if=_is_none)
    mon_fsstatus: str | None = Field(default=None, exclude_if=_is_none)
    mon_hbstatus: str | None = Field(default=None, exclude_if=_is_none)
    mon_ipstatus: str | None = Field(default=None, exclude_if=_is_none)
    mon_sharestatus: str | None = Field(default=None, exclude_if=_is_none)
    mon_syncstatus: str | None = Field(default=None, exclude_if=_is_none)


class ServiceInstanceStatusHistoryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    svcname: str
    svc_id: str | None = Field(default=None, exclude_if=_is_none)
    service: ServiceRow = Field(
        default_factory=ServiceRow,
        description="Current service state used as context for the instance history.",
    )
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ServiceInstanceStatusHistoryRow]


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

from pydantic import BaseModel, ConfigDict, Field, model_validator

from opensvc_collector_mcp.models.pagination import Pagination

from ._common import ServiceNameRequest, _is_none


class ServiceComplianceStatusRequest(ServiceNameRequest):
    filters: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Exact-match service compliance status filters. Keys can be "
            "run_module, run_status, run_action, node_id, rset_md5, id, "
            "or their comp_status.<field> form."
        ),
        examples=[{"run_status": "1"}, {"run_module": "aits.outils.controlm"}],
    )
    run_module: str | None = Field(
        default=None, description="Exact compliance module filter."
    )
    run_status: int | None = Field(
        default=None,
        ge=0,
        description="Exact compliance run status filter. In this Collector, 0 is OK and non-zero is not OK.",
    )
    run_action: str | None = Field(
        default=None, description="Exact compliance run action filter."
    )
    node_id: str | None = Field(
        default=None, description="Exact Collector node uuid filter."
    )
    rset_md5: str | None = Field(
        default=None, description="Exact compliance ruleset hash filter."
    )
    props: str | None = Field(
        default=None,
        description=(
            "Comma-separated compliance status properties to return. Defaults to "
            "module, action, status, date, node, ruleset hash, and id. run_log "
            "is automatically requested when preview or full log output is enabled."
        ),
    )
    orderby: str | None = Field(
        default="~run_date",
        description="Collector ordering expression. Keep it unchanged between pages.",
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=1000,
        description="Maximum number of compliance status rows in this page.",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of matching compliance status rows to skip.",
    )
    include_run_log: bool = Field(
        default=False,
        description="Include full Collector run_log values. Disabled by default because logs can be large.",
    )
    include_run_log_preview: bool = Field(
        default=True,
        description="Include a truncated run_log_preview when run_log is available.",
    )
    run_log_max_chars: int = Field(
        default=1000,
        ge=0,
        le=20000,
        description="Maximum characters kept in run_log_preview.",
    )

    @model_validator(mode="after")
    def normalize_filters(self) -> "ServiceComplianceStatusRequest":
        self.filters = {
            key.strip(): value.strip()
            for key, value in self.filters.items()
            if key.strip() and value.strip()
        }
        return self

    def merged_filters(self) -> dict[str, str]:
        merged = dict(self.filters)
        for field in ("run_module", "run_action", "node_id", "rset_md5"):
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
        if self.run_status is not None:
            value = str(self.run_status)
            existing = merged.get("run_status")
            if existing is not None and existing != value:
                raise ValueError("Conflicting filter values for 'run_status'")
            merged["run_status"] = value
        return merged


class ServiceComplianceLogsRequest(ServiceNameRequest):
    filters: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Exact-match service compliance log filters. Keys can be "
            "run_module, run_status, run_action, node_id, rset_md5, id, "
            "or their comp_log.<field> form."
        ),
        examples=[{"run_status": "1"}, {"run_module": "aits.outils.controlm"}],
    )
    run_module: str | None = Field(
        default=None, description="Exact compliance module filter."
    )
    run_status: int | None = Field(
        default=None,
        ge=0,
        description="Exact compliance run status filter. In this Collector, 0 is OK and non-zero is not OK.",
    )
    run_action: str | None = Field(
        default=None, description="Exact compliance run action filter."
    )
    node_id: str | None = Field(
        default=None, description="Exact Collector node uuid filter."
    )
    rset_md5: str | None = Field(
        default=None, description="Exact compliance ruleset hash filter."
    )
    props: str | None = Field(
        default=None,
        description=(
            "Comma-separated compliance log properties to return. Defaults to "
            "module, action, status, date, node, ruleset hash, and id. run_log "
            "is automatically requested when preview or full log output is enabled."
        ),
    )
    orderby: str | None = Field(
        default="~run_date",
        description="Collector ordering expression. Keep it unchanged between pages.",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=1000,
        description="Maximum number of compliance log rows in this page.",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of matching compliance log rows to skip.",
    )
    include_run_log: bool = Field(
        default=False,
        description="Include full Collector run_log values. Disabled by default because logs can be large.",
    )
    include_run_log_preview: bool = Field(
        default=True,
        description="Include a truncated run_log_preview when run_log is available.",
    )
    run_log_max_chars: int = Field(
        default=1000,
        ge=0,
        le=20000,
        description="Maximum characters kept in run_log_preview.",
    )

    @model_validator(mode="after")
    def normalize_filters(self) -> "ServiceComplianceLogsRequest":
        self.filters = {
            key.strip(): value.strip()
            for key, value in self.filters.items()
            if key.strip() and value.strip()
        }
        return self

    def merged_filters(self) -> dict[str, str]:
        merged = dict(self.filters)
        for field in ("run_module", "run_action", "node_id", "rset_md5"):
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
        if self.run_status is not None:
            value = str(self.run_status)
            existing = merged.get("run_status")
            if existing is not None and existing != value:
                raise ValueError("Conflicting filter values for 'run_status'")
            merged["run_status"] = value
        return merged


class ServiceComplianceStatusRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | str | None = Field(
        default=None,
        description="Collector compliance status row id.",
        exclude_if=_is_none,
    )
    svc_id: str | None = Field(
        default=None,
        description="Collector service uuid.",
        exclude_if=_is_none,
    )
    node_id: str | None = Field(
        default=None,
        description="Collector node uuid where the compliance check ran.",
        exclude_if=_is_none,
    )
    nodename: str | None = Field(
        default=None,
        description="Node name resolved from node_id when available.",
        exclude_if=_is_none,
    )
    run_module: str | None = Field(
        default=None,
        description="Compliance module name.",
        exclude_if=_is_none,
    )
    run_action: str | None = Field(
        default=None,
        description="Compliance action, usually check or fix.",
        exclude_if=_is_none,
    )
    run_status: int | str | None = Field(
        default=None,
        description="Compliance run status. In this Collector, 0 is OK and non-zero is not OK.",
        exclude_if=_is_none,
    )
    run_date: str | None = Field(
        default=None,
        description="Compliance run timestamp.",
        exclude_if=_is_none,
    )
    rset_md5: str | None = Field(
        default=None,
        description="Compliance ruleset hash associated with this run.",
        exclude_if=_is_none,
    )
    run_log: str | None = Field(
        default=None,
        description="Full compliance run log when include_run_log is true.",
        exclude_if=_is_none,
    )
    run_log_preview: str | None = Field(
        default=None,
        description="Truncated compliance run log preview.",
        exclude_if=_is_none,
    )
    run_log_truncated: bool | None = Field(
        default=None,
        description="Whether run_log_preview was truncated.",
        exclude_if=_is_none,
    )


class ServiceComplianceLogRow(ServiceComplianceStatusRow):
    pass


class ServiceCompliancePageSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_names_resolved: bool
    node_name_count: int
    unresolved_node_ids: list[str]
    ok_count: int = Field(description="OK runs in this page only.")
    error_count: int = Field(description="Non-OK runs in this page only.")
    unknown_count: int = Field(description="Runs with unknown status in this page.")
    failed_modules: list[str] = Field(
        description="Distinct failed modules found in this page."
    )


class ServiceComplianceLogsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    svcname: str
    pagination: Pagination
    summary: ServiceCompliancePageSummary
    data: list[ServiceComplianceLogRow]


class ServiceComplianceStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    svcname: str
    pagination: Pagination
    summary: ServiceCompliancePageSummary
    data: list[ServiceComplianceStatusRow]

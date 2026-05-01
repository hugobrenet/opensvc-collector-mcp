from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ComplianceStatusRequest(BaseModel):
    filters: dict[str, str] = Field(
        default_factory=dict,
        description="Exact-match Collector filters. Keys can be raw Collector compliance status properties.",
    )
    run_module: str | None = Field(
        default=None,
        description="Exact compliance module name to filter on, for example aits.nodes.opensvc.tags.",
    )
    run_status: int | str | None = Field(
        default=None,
        description="Compliance run status to filter on. Observed values: 0 means OK, 1 means error/NOK.",
    )
    run_action: str | None = Field(
        default=None,
        description="Compliance action to filter on when known.",
    )
    node_id: str | None = Field(
        default=None,
        description="Collector node id to filter compliance status rows.",
    )
    svc_id: str | None = Field(
        default=None,
        description="Collector service id to filter compliance status rows.",
    )
    rset_md5: str | None = Field(
        default=None,
        description="Ruleset md5 identifier to filter compliance status rows.",
    )
    props: str | None = Field(
        default=None,
        description="Comma-separated Collector compliance status properties to return.",
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=1000,
        description="Maximum number of compliance status rows to return.",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of matching compliance status rows to skip.",
    )
    latest: bool = Field(
        default=True,
        description="Return the latest/current status page by forcing offset 0 and run_date descending.",
    )
    latest_first: bool = Field(
        default=True,
        description="Sort returned rows newest first.",
    )
    include_run_log: bool = Field(
        default=False,
        description="Include full run_log in rows. Keep false unless the user explicitly needs full logs.",
    )
    include_run_log_preview: bool = Field(
        default=False,
        description="Include bounded run_log_preview for quick diagnostics without returning full logs.",
    )
    run_log_max_chars: int = Field(
        default=1000,
        ge=0,
        le=20000,
        description="Maximum characters returned in run_log_preview.",
    )

    @model_validator(mode="after")
    def normalize_status_filters(self) -> "ComplianceStatusRequest":
        self.filters = {
            key.strip(): value.strip()
            for key, value in self.filters.items()
            if key.strip() and value.strip()
        }
        for field_name in (
            "run_module",
            "run_action",
            "node_id",
            "svc_id",
            "rset_md5",
            "props",
        ):
            value = getattr(self, field_name)
            if isinstance(value, str):
                setattr(self, field_name, value.strip() or None)
        if isinstance(self.run_status, str):
            self.run_status = self.run_status.strip() or None
        return self


class ComplianceStatusRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | str | None = Field(
        default=None, description="Collector compliance run id."
    )
    svc_id: str | None = Field(default=None, description="Collector service id.")
    svcname: str | None = Field(
        default=None, description="OpenSVC service name when available."
    )
    node_id: str | None = Field(default=None, description="Collector node id.")
    nodename: str | None = Field(
        default=None, description="OpenSVC node name when available."
    )
    run_module: str | None = Field(default=None, description="Compliance module name.")
    run_action: str | None = Field(default=None, description="Compliance action.")
    run_status: int | str | None = Field(
        default=None, description="Compliance run status. 0 is OK, 1 is error/NOK."
    )
    run_date: str | None = Field(default=None, description="Compliance run date.")
    rset_md5: str | None = Field(default=None, description="Ruleset md5 identifier.")
    run_log_preview: str | None = Field(
        default=None, description="Bounded run log preview when requested."
    )
    run_log_truncated: bool | None = Field(
        default=None, description="Whether run_log_preview was truncated."
    )
    run_log: str | None = Field(
        default=None, description="Full run log when explicitly requested."
    )


class ComplianceLogsRequest(ComplianceStatusRequest):
    filters: dict[str, str] = Field(
        default_factory=dict,
        description="Exact-match Collector filters. Keys can be raw Collector compliance log properties.",
    )
    node_id: str | None = Field(
        default=None,
        description="Collector node id required to scope historical compliance logs, unless svc_id is provided.",
    )
    svc_id: str | None = Field(
        default=None,
        description="Collector service id required to scope historical compliance logs, unless node_id is provided.",
    )
    props: str | None = Field(
        default=None,
        description="Comma-separated Collector compliance log properties to return.",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=1000,
        description="Maximum number of historical compliance log rows to return.",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of matching historical compliance log rows to skip.",
    )
    latest: bool = Field(
        default=False,
        description="When true, force the newest log page by using offset 0. Keep false to paginate historical logs.",
    )
    include_run_log_preview: bool = Field(
        default=True,
        description="Include bounded run_log_preview by default for historical log diagnostics.",
    )

    @model_validator(mode="after")
    def require_log_scope(self) -> "ComplianceLogsRequest":
        has_node = bool(self.node_id)
        has_service = bool(self.svc_id)
        for field in self.filters:
            if field.rsplit(".", 1)[-1] == "node_id":
                has_node = True
            if field.rsplit(".", 1)[-1] == "svc_id":
                has_service = True
        if not has_node and not has_service:
            raise ValueError(
                "node_id or svc_id must be provided to query compliance logs"
            )
        return self


class ComplianceLogsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ComplianceStatusRow]


class ComplianceRunDetailRequest(BaseModel):
    source: Literal["status", "logs"] = Field(
        description="Compliance run source collection: status for current status runs, logs for historical log runs.",
        examples=["logs"],
    )
    run_id: int | str = Field(
        description="Collector compliance run id returned by get_compliance_status or get_compliance_logs.",
        examples=[65120347],
    )
    props: str | None = Field(
        default=None,
        description="Comma-separated Collector compliance run properties to return.",
    )
    include_run_log: bool = Field(
        default=False,
        description="Include full run_log. Keep false unless the user explicitly needs the complete raw log.",
    )
    include_run_log_preview: bool = Field(
        default=True,
        description="Include bounded run_log_preview for quick diagnostics.",
    )
    run_log_max_chars: int = Field(
        default=2000,
        ge=0,
        le=20000,
        description="Maximum characters returned in run_log_preview.",
    )

    @model_validator(mode="after")
    def normalize_detail_request(self) -> "ComplianceRunDetailRequest":
        if isinstance(self.run_id, str):
            self.run_id = self.run_id.strip()
        if not str(self.run_id).strip():
            raise ValueError("run_id must not be empty")
        if isinstance(self.props, str):
            self.props = self.props.strip() or None
        return self


class ComplianceRunDetailResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ComplianceStatusRow]


class ComplianceStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ComplianceStatusRow]

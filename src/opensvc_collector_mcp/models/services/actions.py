from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ._common import ServiceNameRequest, _is_none


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

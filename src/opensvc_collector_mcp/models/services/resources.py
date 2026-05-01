from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ._common import ServiceRelationCollectionRequest, _is_none


class ServiceResourceStatusRequest(ServiceRelationCollectionRequest):
    filters: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Exact-match runtime resource filters. Keys can be rid, node_id, "
            "vmname, res_type, res_status, res_disable, res_optional, "
            "res_monitor, or their resmon.<field> form."
        ),
        examples=[{"res_status": "down"}, {"rid": "container#0"}],
    )
    rid: str | None = Field(
        default=None, description="Exact OpenSVC resource id filter."
    )
    node_id: str | None = Field(
        default=None, description="Exact Collector node uuid filter."
    )
    vmname: str | None = Field(
        default=None,
        description="Exact VM or encapsulated instance name filter.",
    )
    res_type: str | None = Field(
        default=None, description="Exact resource type filter."
    )
    res_status: str | None = Field(
        default=None, description="Exact runtime resource status filter."
    )
    res_disable: str | None = Field(
        default=None, description="Exact resource disabled flag filter."
    )
    res_optional: str | None = Field(
        default=None, description="Exact resource optional flag filter."
    )
    res_monitor: str | None = Field(
        default=None, description="Exact resource monitor flag filter."
    )
    @model_validator(mode="after")
    def normalize_filters(self) -> "ServiceResourceStatusRequest":
        self.filters = {
            key.strip(): value.strip()
            for key, value in self.filters.items()
            if key.strip() and value.strip()
        }
        return self

    def merged_filters(self) -> dict[str, str]:
        merged = dict(self.filters)
        for field in (
            "rid",
            "node_id",
            "vmname",
            "res_type",
            "res_status",
            "res_disable",
            "res_optional",
            "res_monitor",
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


class ServiceResourceStatusRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | str | None = Field(
        default=None,
        description="Collector runtime resource row id.",
        exclude_if=_is_none,
    )
    svc_id: str | None = Field(
        default=None,
        description="Collector service uuid.",
        exclude_if=_is_none,
    )
    node_id: str | None = Field(
        default=None,
        description="Collector node uuid where this resource status was reported.",
        exclude_if=_is_none,
    )
    nodename: str | None = Field(
        default=None,
        description="Node name resolved from node_id when available.",
        exclude_if=_is_none,
    )
    rid: str | None = Field(
        default=None,
        description="OpenSVC resource identifier, for example container#0 or disk#0.",
        exclude_if=_is_none,
    )
    vmname: str | None = Field(
        default=None,
        description="VM or encapsulated instance name associated with the resource.",
        exclude_if=_is_none,
    )
    res_type: str | None = Field(
        default=None,
        description="OpenSVC resource type, for example container.docker or disk.vg.",
        exclude_if=_is_none,
    )
    res_status: str | None = Field(
        default=None,
        description="Runtime resource status as reported by Collector.",
        exclude_if=_is_none,
    )
    res_desc: str | None = Field(
        default=None,
        description="Human-readable resource description.",
        exclude_if=_is_none,
    )
    res_disable: str | bool | None = Field(
        default=None,
        description="Resource disabled flag as reported by Collector.",
        exclude_if=_is_none,
    )
    res_optional: str | bool | None = Field(
        default=None,
        description="Resource optional flag as reported by Collector.",
        exclude_if=_is_none,
    )
    res_monitor: str | bool | None = Field(
        default=None,
        description="Resource monitor flag as reported by Collector.",
        exclude_if=_is_none,
    )
    changed: str | None = Field(
        default=None,
        description="Timestamp when the runtime resource state last changed.",
        exclude_if=_is_none,
    )
    updated: str | None = Field(
        default=None,
        description="Collector update timestamp for this resource row.",
        exclude_if=_is_none,
    )
    res_log: str | None = Field(
        default=None,
        description="Runtime resource log when explicitly requested in props.",
        exclude_if=_is_none,
    )


class ServiceResourceStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    svcname: str
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ServiceResourceStatusRow]


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

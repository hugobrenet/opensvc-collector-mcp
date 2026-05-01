from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ._common import ServiceNameRequest, _is_none


class ServiceHbasRequest(ServiceNameRequest):
    props: str | None = Field(
        default=None,
        description=(
            "Comma-separated service HBA properties to return. Defaults to a "
            "compact flat HBA view with node, HBA id, HBA type, and update time."
        ),
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
    node_id: str | None = Field(
        default=None, description="Exact Collector node uuid filter."
    )
    tgt_id: str | None = Field(
        default=None, description="Exact storage target identifier filter."
    )
    array_name: str | None = Field(
        default=None, description="Exact storage array name filter."
    )
    props: str | None = Field(
        default=None,
        description=(
            "Comma-separated service target properties to return. Defaults to a "
            "compact flat target view with node, HBA, target, and array fields."
        ),
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
    max_disks: int = Field(
        default=10000,
        ge=1,
        le=100000,
        description="Maximum number of service disk rows the tool may return.",
    )


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

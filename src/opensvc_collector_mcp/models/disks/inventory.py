from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


def _is_none(value: object) -> bool:
    return value is None


class DiskFilterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filters: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Exact-match disk property filters. Keys must be Collector disk "
            "properties returned by list_disk_props. Common filters include "
            "node_id, svc_id, app_id, disk_id, disk_local, and array_name."
        ),
        examples=[{"node_id": "NODE-ID"}],
    )
    node_id: str | None = Field(default=None, description="Exact Collector node uuid.")
    svc_id: str | None = Field(default=None, description="Exact Collector service uuid.")
    app_id: str | None = Field(default=None, description="Exact Collector app row id.")
    disk_id: str | None = Field(
        default=None,
        description="Exact stable Collector disk identifier.",
    )
    disk_local: str | None = Field(
        default=None,
        description="Exact Collector disk_local value, for example true or false.",
    )
    disk_group: str | None = Field(default=None, description="Exact storage disk group.")
    disk_arrayid: str | None = Field(
        default=None,
        description="Exact storage array identifier from diskinfo.",
    )
    array_name: str | None = Field(default=None, description="Exact storage array name.")

    @model_validator(mode="after")
    def normalize_filters(self) -> "DiskFilterRequest":
        self.filters = {
            key.strip(): value.strip()
            for key, value in self.filters.items()
            if key.strip() and value.strip()
        }
        return self

    def merged_filters(self) -> dict[str, str]:
        merged = dict(self.filters)
        for field in (
            "node_id",
            "svc_id",
            "app_id",
            "disk_id",
            "disk_local",
            "disk_group",
            "disk_arrayid",
            "array_name",
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


class CountDisksRequest(DiskFilterRequest):
    search: str | None = Field(
        default=None,
        description="Collector full-text search expression when supported by /disks.",
    )


class CountDisksResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    count: int | None = Field(description="Number of matching disk rows.")
    filters: dict[str, str] = Field(default_factory=dict)
    search: str | None = Field(default=None)


class ListDisksRequest(DiskFilterRequest):
    props: str | None = Field(
        default=None,
        description=(
            "Comma-separated disk properties to include in the response. "
            "Defaults to a compact flat disk inventory view using Collector "
            "table-prefixed props and aliases."
        ),
    )
    orderby: str | None = Field(
        default=None,
        description="Collector orderby expression when supported by /disks.",
    )
    search: str | None = Field(
        default=None,
        description="Collector full-text search expression when supported by /disks.",
    )
    limit: int = Field(default=20, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class GetDiskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    disk: str = Field(
        min_length=1,
        description=(
            "Stable Collector disk_id selector used by /disks/<id>. "
            "This is not the svcdisks.id or diskinfo.id row id."
        ),
        examples=["DISK-ID"],
    )
    props: str | None = Field(
        default=None,
        description="Comma-separated disk properties to include in the response.",
    )


class DiskPropsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    count: int = Field(description="Number of disk properties exposed by Collector.")
    available_props: list[str] = Field(
        description="Raw Collector disk properties, including table prefixes."
    )
    disk_props: list[str] = Field(
        description="Disk property names without svcdisks, diskinfo, or stor_array prefixes."
    )


class DiskRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | str | None = Field(default=None, exclude_if=_is_none)
    node_id: str | None = Field(default=None, exclude_if=_is_none)
    svc_id: str | None = Field(default=None, exclude_if=_is_none)
    app_id: int | str | None = Field(default=None, exclude_if=_is_none)
    disk_id: str | None = Field(default=None, exclude_if=_is_none)
    disk_size: int | float | str | None = Field(default=None, exclude_if=_is_none)
    disk_used: int | float | str | None = Field(default=None, exclude_if=_is_none)
    disk_local: bool | str | None = Field(default=None, exclude_if=_is_none)
    disk_dg: str | None = Field(default=None, exclude_if=_is_none)
    disk_vendor: str | None = Field(default=None, exclude_if=_is_none)
    disk_model: str | None = Field(default=None, exclude_if=_is_none)
    disk_region: str | None = Field(default=None, exclude_if=_is_none)
    disk_updated: str | None = Field(default=None, exclude_if=_is_none)
    diskinfo_id: int | str | None = Field(default=None, exclude_if=_is_none)
    diskinfo_disk_id: str | None = Field(default=None, exclude_if=_is_none)
    disk_name: str | None = Field(default=None, exclude_if=_is_none)
    disk_devid: str | None = Field(default=None, exclude_if=_is_none)
    disk_alloc: int | float | str | None = Field(default=None, exclude_if=_is_none)
    disk_level: int | str | None = Field(default=None, exclude_if=_is_none)
    disk_raid: str | None = Field(default=None, exclude_if=_is_none)
    disk_group: str | None = Field(default=None, exclude_if=_is_none)
    disk_arrayid: str | None = Field(default=None, exclude_if=_is_none)
    disk_controller: str | None = Field(default=None, exclude_if=_is_none)
    disk_created: str | None = Field(default=None, exclude_if=_is_none)
    diskinfo_updated: str | None = Field(default=None, exclude_if=_is_none)
    array_id: int | str | None = Field(default=None, exclude_if=_is_none)
    array_name: str | None = Field(default=None, exclude_if=_is_none)
    array_model: str | None = Field(default=None, exclude_if=_is_none)
    array_firmware: str | None = Field(default=None, exclude_if=_is_none)
    svcdisks: dict[str, Any] | None = Field(default=None, exclude_if=_is_none)
    diskinfo: dict[str, Any] | None = Field(default=None, exclude_if=_is_none)
    stor_array: dict[str, Any] | None = Field(default=None, exclude_if=_is_none)


class DiskRowsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[DiskRow]


class DiskDetailResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    disk: str
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[DiskRow]

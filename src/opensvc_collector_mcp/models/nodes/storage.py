from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class NodeDiskEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    svc_id: str | None = None
    disk_size: Any = None
    disk_dg: str | None = None
    disk_vendor: str | None = None
    disk_model: str | None = None
    app_id: str | None = None
    disk_id: str | None = None
    id: int | None = None
    node_id: str | None = None
    disk_local: Any = None
    disk_used: Any = None
    disk_region: str | None = None
    disk_updated: str | None = None
    disk_created: str | None = None
    disk_alloc: Any = None
    disk_devid: str | None = None
    disk_level: str | None = None
    disk_raid: str | None = None
    disk_group: str | None = None
    disk_arrayid: str | None = None
    disk_controller: str | None = None
    disk_name: str | None = None
    array_comment: str | None = None
    array_updated: str | None = None
    array_model: str | None = None
    array_cache: str | None = None
    array_firmware: str | None = None
    array_level: str | None = None
    array_name: str | None = None


class NodeDisksResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[NodeDiskEntry]

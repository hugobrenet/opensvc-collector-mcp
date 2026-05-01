from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class NodeDiskEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    svc_id: str | None = Field(
        default=None,
        description="Collector service uuid attached to this disk row, when any.",
    )
    disk_size: Any = Field(
        default=None, description="Disk size in MB as exposed by Collector."
    )
    disk_dg: str | None = Field(
        default=None,
        description="Disk device group or storage identifier when returned.",
    )
    disk_vendor: str | None = Field(
        default=None, description="Disk vendor, for example EMC or HPE."
    )
    disk_model: str | None = Field(
        default=None, description="Disk model, for example SYMMETRIX or LOGICAL VOLUME."
    )
    app_id: str | None = Field(
        default=None,
        description="Collector application id associated with the disk row.",
    )
    disk_id: str | None = Field(
        default=None,
        description="Stable Collector disk identifier. Use this to deduplicate rows.",
    )
    id: int | None = Field(default=None, description="Collector disk row id.")
    node_id: str | None = Field(default=None, description="Collector node uuid.")
    disk_local: Any = Field(
        default=None,
        description="Whether Collector marks this disk as local to the node. false usually means SAN/shared storage.",
    )
    disk_used: Any = Field(
        default=None,
        description="Used or presented disk size in MB as exposed by Collector.",
    )
    disk_region: str | None = Field(
        default=None, description="Disk region or allocation region when returned."
    )
    disk_updated: str | None = Field(
        default=None, description="Collector disk update timestamp."
    )
    disk_created: str | None = Field(
        default=None, description="Collector disk creation timestamp when available."
    )
    disk_alloc: Any = Field(
        default=None,
        description="Allocated disk size or allocation metric in MB when returned by diskinfo.",
    )
    disk_devid: str | None = Field(
        default=None,
        description="Storage device identifier from diskinfo, such as a PowerMax device id.",
    )
    disk_level: str | None = Field(
        default=None, description="Collector disk hierarchy level when returned."
    )
    disk_raid: str | None = Field(
        default=None, description="RAID or storage layout information."
    )
    disk_group: str | None = Field(
        default=None, description="Storage disk group or pool."
    )
    disk_arrayid: str | None = Field(
        default=None, description="Storage array identifier associated with this disk."
    )
    disk_controller: str | None = Field(
        default=None, description="Disk controller identifier when returned."
    )
    disk_name: str | None = Field(
        default=None,
        description="Human-readable disk or LUN name when known by Collector.",
    )
    array_comment: str | None = Field(
        default=None, description="Storage array comment."
    )
    array_updated: str | None = Field(
        default=None, description="Storage array update timestamp."
    )
    array_model: str | None = Field(default=None, description="Storage array model.")
    array_cache: str | None = Field(
        default=None, description="Storage array cache size or metric when returned."
    )
    array_firmware: str | None = Field(
        default=None, description="Storage array firmware."
    )
    array_level: str | None = Field(
        default=None,
        description="Collector storage array hierarchy level when returned.",
    )
    array_name: str | None = Field(default=None, description="Storage array name.")
    svcdisks: dict[str, Any] | None = Field(
        default=None,
        description="Raw Collector svcdisks object. It can contain disk_size, disk_used, disk_local, disk_id, node_id, and service attachment fields.",
    )
    diskinfo: dict[str, Any] | None = Field(
        default=None,
        description="Raw Collector diskinfo object. It can contain disk_name, disk_devid, disk_arrayid, disk_group, disk_raid, and allocation fields.",
    )
    stor_array: dict[str, Any] | None = Field(
        default=None,
        description="Raw Collector stor_array object. It can contain array_name, array_model, firmware, cache, and comment fields.",
    )


class NodeDisksResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[NodeDiskEntry]

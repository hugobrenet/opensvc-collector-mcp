from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class NodeNetworkEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mac: str | None = None
    net_team_responsible: str | None = None
    intf: str | None = None
    addr: str | None = None
    prio: int | None = None
    net_gateway: str | None = None
    net_comment: str | None = None
    net_end: str | None = None
    net_netmask: int | None = None
    mask: str | None = None
    net_network: str | None = None
    addr_type: str | None = None
    net_broadcast: str | None = None
    net_pvid: int | None = None
    net_begin: str | None = None
    flag_deprecated: bool | None = None
    addr_updated: str | None = None
    net_id: int | None = None
    net_name: str | None = None


class NodeNetworkResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[NodeNetworkEntry]

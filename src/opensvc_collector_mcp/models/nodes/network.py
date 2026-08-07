from pydantic import BaseModel, ConfigDict

from opensvc_collector_mcp.models.pagination import Pagination


class NodeNetworkEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

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
    pagination: Pagination
    data: list[NodeNetworkEntry]

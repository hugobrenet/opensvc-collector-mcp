from pydantic import BaseModel, ConfigDict

from opensvc_collector_mcp.models.pagination import Pagination

from ._common import NodeRelationRequest


class NodeServicesRequest(NodeRelationRequest):
    pass


class NodeService(BaseModel):
    model_config = ConfigDict(extra="allow")

    nodename: str | None = None
    svcname: str | None = None
    svc_status: str | None = None
    svc_env: str | None = None
    svc_app: str | None = None
    svc_topology: str | None = None
    mon_vmname: str | None = None
    mon_availstatus: str | None = None


class NodeServicesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str
    pagination: Pagination
    data: list[NodeService]

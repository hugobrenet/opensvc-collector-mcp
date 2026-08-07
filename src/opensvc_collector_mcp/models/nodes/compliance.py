from pydantic import BaseModel, ConfigDict

from opensvc_collector_mcp.models.pagination import Pagination


class NodeComplianceEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    svc_id: str | None = None
    run_module: str | None = None
    run_date: str | None = None
    run_log: str | None = None
    node_id: str | None = None
    run_action: str | None = None
    rset_md5: str | None = None
    run_status: int | None = None
    id: int | None = None


class NodeComplianceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str
    pagination: Pagination
    data: list[NodeComplianceEntry]

from typing import Any

from pydantic import BaseModel, ConfigDict

from opensvc_collector_mcp.models.pagination import Pagination


class NodeTagsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str
    pagination: Pagination
    data: list[dict[str, Any]]

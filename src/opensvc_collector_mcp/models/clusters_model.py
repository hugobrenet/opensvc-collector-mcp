from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ClusterNameRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cluster_name: str = Field(
        min_length=1,
        description="Exact OpenSVC Collector cluster name.",
        examples=["mcp-cluster-a"],
    )


class ClusterNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str
    cluster_name: str | None = None


class ClusterNodesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cluster_name: str
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ClusterNode]

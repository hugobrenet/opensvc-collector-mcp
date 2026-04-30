from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class NodeCluster(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str | None = None
    name: str | None = None


class NodeClusterResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str
    cluster: NodeCluster | None = None
    raw: dict[str, Any] = Field(default_factory=dict)

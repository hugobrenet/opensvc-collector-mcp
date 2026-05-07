from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class NodeTagsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[dict[str, Any]]

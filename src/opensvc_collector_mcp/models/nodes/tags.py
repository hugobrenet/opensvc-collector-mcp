from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TagNameRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tag_name: str = Field(
        min_length=1,
        description="Exact OpenSVC Collector tag name.",
        examples=["test"],
    )


class NodeTagsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[dict[str, Any]]


class NodesByTagResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tag_name: str
    tag_id: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[dict[str, Any]]


class NodesWithoutTagResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tag_name: str
    tag_id: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[dict[str, Any]]

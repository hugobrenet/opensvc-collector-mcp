from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ClusterNameRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cluster_name: str = Field(
        min_length=1,
        description="Exact OpenSVC Collector cluster name.",
        examples=["mcp-cluster-a"],
    )
    filters: dict[str, str] = Field(
        default_factory=dict,
        description="Additional exact-match node filters for the cluster member listing.",
    )
    props: str | None = Field(
        default=None,
        description="Comma-separated node properties to return.",
    )
    orderby: str | None = Field(
        default=None,
        description="Collector orderby expression, for example nodename or ~updated.",
    )
    search: str | None = Field(
        default=None,
        description="Collector full-text search expression when supported by /nodes.",
    )
    limit: int = Field(default=20, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def normalize_filters(self) -> "ClusterNameRequest":
        self.filters = {
            key.strip(): value.strip()
            for key, value in self.filters.items()
            if key.strip() and value.strip()
        }
        return self


class ClusterNode(BaseModel):
    model_config = ConfigDict(extra="allow")

    nodename: str
    cluster_name: str | None = None


class ClusterNodesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cluster_name: str
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ClusterNode]

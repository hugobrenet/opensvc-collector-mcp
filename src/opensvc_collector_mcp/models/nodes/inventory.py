from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class NodeFilterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filters: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Exact-match node property filters. Keys must be Collector node "
            "properties returned by list_node_props."
        ),
        examples=[{"status": "warn", "loc_city": "Lab City"}],
    )
    status: str | None = Field(default=None, description="Exact node status.")
    asset_env: str | None = Field(default=None, description="Exact asset environment.")
    node_env: str | None = Field(default=None, description="Exact node environment.")
    loc_city: str | None = Field(default=None, description="Exact node city.")
    loc_country: str | None = Field(default=None, description="Exact node country.")
    team_responsible: str | None = Field(default=None, description="Exact responsible team.")
    app: str | None = Field(default=None, description="Exact application name.")
    os_name: str | None = Field(default=None, description="Exact operating system name.")

    @model_validator(mode="after")
    def normalize_filters(self) -> "NodeFilterRequest":
        self.filters = {
            key.strip(): value.strip()
            for key, value in self.filters.items()
            if key.strip() and value.strip()
        }
        return self

    def merged_filters(self) -> dict[str, str]:
        merged = dict(self.filters)
        for field in (
            "status",
            "asset_env",
            "node_env",
            "loc_city",
            "loc_country",
            "team_responsible",
            "app",
            "os_name",
        ):
            value = getattr(self, field)
            if value is None:
                continue
            value = value.strip()
            if not value:
                continue
            existing = merged.get(field)
            if existing is not None and existing != value:
                raise ValueError(f"Conflicting filter values for {field!r}")
            merged[field] = value
        return merged


class NodeCollectionRequest(NodeFilterRequest):
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
    limit: int = Field(
        default=20,
        ge=1,
        le=1000,
        description="Maximum number of nodes to return.",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of matching nodes to skip.",
    )


class ListNodesRequest(NodeCollectionRequest):
    nodename_contains: str | None = Field(
        default=None,
        description="Case-insensitive substring to find in nodenames.",
    )
    max_scan: int = Field(
        default=5000,
        ge=1,
        le=50000,
        description="Maximum candidate nodes to scan when using nodename_contains.",
    )


class CountNodesRequest(NodeFilterRequest):
    pass


class NodePropsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    count: int
    available_props: list[str]
    node_props: list[str]


class NodeRowsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[dict[str, Any]]


class CountNodesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    count: int | None
    filters: dict[str, str]

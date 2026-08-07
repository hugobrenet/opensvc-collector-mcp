from pydantic import BaseModel, ConfigDict, Field, model_validator


class NodeNameRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str = Field(
        min_length=1,
        description="Exact OpenSVC Collector nodename.",
        examples=["lab-node-01"],
    )


class NodeSelector(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_id: str | None = Field(
        default=None,
        description="Exact Collector node_id. Provide either node_id or nodename.",
        examples=["NODE-ID"],
    )
    nodename: str | None = Field(
        default=None,
        description=(
            "Exact Collector nodename. MCP resolves it to one node_id and refuses "
            "ambiguous duplicate nodenames. Provide either node_id or nodename."
        ),
        examples=["lab-node-01"],
    )

    @model_validator(mode="after")
    def normalize_selector(self) -> "NodeSelector":
        self.node_id = self.node_id.strip() if self.node_id else None
        self.nodename = self.nodename.strip() if self.nodename else None
        if bool(self.node_id) == bool(self.nodename):
            raise ValueError("provide exactly one node selector: node_id or nodename")
        return self


class NodeIdRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"examples": [{"node_id": "NODE-ID"}]},
    )

    node_id: str = Field(
        description=(
            "Required stable Collector node_id execution selector. Never pass a "
            "nodename as node_id. Resolve human-readable names with get_node "
            "before calling this tool."
        ),
        min_length=1,
        examples=["NODE-ID"],
    )

    @model_validator(mode="after")
    def normalize_node_id(self) -> "NodeIdRequest":
        self.node_id = self.node_id.strip()
        if not self.node_id:
            raise ValueError("node_id must not be empty")
        return self


class NodeRelationRequest(NodeNameRequest):
    filters: dict[str, str] = Field(
        default_factory=dict,
        description="Exact-match Collector filters for this node relation endpoint.",
    )
    props: str | None = Field(
        default=None,
        description="Comma-separated Collector properties to return.",
    )
    orderby: str | None = Field(
        default=None,
        description="Collector orderby expression, for example updated or ~updated.",
    )
    search: str | None = Field(
        default=None,
        description="Collector full-text search expression when supported by the endpoint.",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=1000,
        description="Maximum number of rows to return.",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of matching rows to skip.",
    )

    @model_validator(mode="after")
    def normalize_filters(self) -> "NodeRelationRequest":
        self.filters = {
            key.strip(): value.strip()
            for key, value in self.filters.items()
            if key.strip() and value.strip()
        }
        return self

    def merged_filters(self) -> dict[str, str]:
        return dict(self.filters)

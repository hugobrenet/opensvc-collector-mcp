from pydantic import BaseModel, ConfigDict, Field, model_validator

from opensvc_collector_mcp.models.common import ToolConfirmation


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


class ConfirmedNodeIdRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "node_id": "NODE-ID",
                    "confirm_node_id": "NODE-ID",
                    "confirm_nodename": "lab-node-01",
                    "confirmation": {
                        "phrase": "ACTION node NODE-ID lab-node-01",
                    },
                }
            ]
        },
    )

    node_id: str = Field(
        description=(
            "Required execution selector. Never pass nodename as node_id. If the "
            "user provided only a nodename, first call get_node to resolve exactly "
            "one Collector node_id, then call this tool with that resolved node_id. "
            "This selector must match confirm_node_id."
        ),
        min_length=1,
        examples=["NODE-ID"],
    )
    confirm_node_id: str = Field(
        description=(
            "Correlation confirmation value read from the resolved node snapshot. "
            "Required before executing the tool. This is not a second selector. "
            "It must match node_id."
        ),
        min_length=1,
        examples=["NODE-ID"],
    )
    confirm_nodename: str = Field(
        description=(
            "Correlation confirmation value read from the resolved node snapshot. "
            "Required before executing the tool. This is not a second selector. "
            "Use this field for the nodename that appears in the human "
            "confirmation phrase."
        ),
        min_length=1,
        examples=["lab-node-01"],
    )
    confirmation: ToolConfirmation = Field(
        description=(
            "Required confirmation gate for this state-changing node tool. Before "
            "calling the tool, resolve the target node with get_node when the user "
            "gave a nodename, generate a concise phrase containing the exact "
            "resolved node_id and nodename, ask the user to repeat it verbatim, "
            "and set this field to that full phrase only when it appears in the "
            "latest user message. The phrase must contain both values, but tool "
            "execution uses node_id only."
        ),
    )

    @model_validator(mode="after")
    def normalize_confirmed_node_id(self) -> "ConfirmedNodeIdRequest":
        self.node_id = self.node_id.strip()
        self.confirm_node_id = self.confirm_node_id.strip()
        self.confirm_nodename = self.confirm_nodename.strip()
        if not self.node_id:
            raise ValueError("node_id must not be empty")
        if not self.confirm_node_id:
            raise ValueError("confirm_node_id must not be empty")
        if not self.confirm_nodename:
            raise ValueError("confirm_nodename must not be empty")
        if self.confirm_node_id != self.node_id:
            raise ValueError("confirm_node_id must match node_id")
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

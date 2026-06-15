from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from opensvc_collector_mcp.models.common import ToolConfirmation


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


class CreateNodeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str = Field(
        description="OpenSVC Collector nodename to submit to POST /nodes.",
        min_length=1,
        examples=["lab-node-01"],
    )
    properties: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Additional node properties to forward to Collector with the "
            "creation request. Do not include node_id or nodename here: "
            "Collector generates node_id, and the explicit nodename field is "
            "always sent as the nodename payload property. Collector validates "
            "the remaining properties."
        ),
        json_schema_extra={
            "propertyNames": {
                "not": {
                    "enum": ["node_id", "nodename"],
                },
            },
        },
        examples=[{"asset_env": "PPR", "loc_city": "Lab City"}],
    )
    confirmation: ToolConfirmation = Field(
        description=(
            "Required confirmation gate for this state-changing tool. Before "
            "calling create_node, summarize the node payload, ask the user to "
            "repeat a concise confirmation phrase verbatim, and set this field "
            "only when that exact phrase appears in the latest user message."
        ),
    )

    @model_validator(mode="after")
    def normalize(self) -> "CreateNodeRequest":
        self.nodename = self.nodename.strip()
        if not self.nodename:
            raise ValueError("nodename must not be empty")
        self.properties = {
            key.strip(): value
            for key, value in self.properties.items()
            if key.strip()
        }
        forbidden = sorted(set(self.properties) & {"node_id", "nodename"})
        if forbidden:
            rejected = ", ".join(forbidden)
            raise ValueError(
                f"create_node properties must not include reserved fields: {rejected}"
            )
        return self


class CreateNodeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str
    submitted_properties: dict[str, Any]
    collector_response: dict[str, Any]
    meta: dict[str, Any] = Field(default_factory=dict)


class DeleteNodeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_id: str = Field(
        description=(
            "Exact Collector node id to delete. Use list_nodes with props "
            "node_id,nodename to resolve duplicate nodenames before deletion."
        ),
        min_length=1,
        examples=["NODE-ID"],
    )
    confirm_node_id: str = Field(
        description="Exact node_id confirmation required before deleting the node.",
        min_length=1,
        examples=["NODE-ID"],
    )
    confirm_nodename: str = Field(
        description=(
            "Exact nodename read from the node snapshot. This is a human safety "
            "confirmation, not the deletion selector."
        ),
        min_length=1,
        examples=["lab-node-01"],
    )
    confirmation: ToolConfirmation = Field(
        description=(
            "Required confirmation gate for this destructive tool. Before calling "
            "delete_node, generate a concise phrase containing the exact node_id "
            "and nodename, ask the user to repeat it verbatim, and set this field "
            "only when that exact phrase appears in the latest user message."
        ),
    )

    @model_validator(mode="after")
    def normalize(self) -> "DeleteNodeRequest":
        self.node_id = self.node_id.strip()
        self.confirm_node_id = self.confirm_node_id.strip()
        self.confirm_nodename = self.confirm_nodename.strip()
        if not self.node_id:
            raise ValueError("node_id must not be empty")
        if not self.confirm_node_id:
            raise ValueError("confirm_node_id must not be empty")
        if self.confirm_node_id != self.node_id:
            raise ValueError("confirm_node_id must match node_id")
        if not self.confirm_nodename:
            raise ValueError("confirm_nodename must not be empty")
        return self


class DeleteNodeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_id: str
    nodename: str
    node: dict[str, Any]
    deleted: bool
    collector_response: dict[str, Any]
    meta: dict[str, Any] = Field(default_factory=dict)


class UpdateNodePropertiesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str = Field(
        description="Exact OpenSVC Collector nodename to update.",
        min_length=1,
        examples=["lab-node-01"],
    )
    properties: dict[str, Any] = Field(
        description=(
            "Node properties to update. The core layer accepts the properties "
            "advertised as writable by the Collector nodes API definition."
        ),
        examples=[{"asset_env": "PPR", "nodename": "lab-node-02"}],
    )
    confirmation: ToolConfirmation = Field(
        description=(
            "Required confirmation gate for this state-changing tool. Before "
            "calling update_node_properties, summarize the exact node and property "
            "changes, ask the user to repeat a concise confirmation phrase "
            "verbatim, and set this field only when that exact phrase appears in "
            "the latest user message."
        ),
    )

    @model_validator(mode="after")
    def normalize(self) -> "UpdateNodePropertiesRequest":
        self.nodename = self.nodename.strip()
        if not self.nodename:
            raise ValueError("nodename must not be empty")
        self.properties = {
            key.strip(): value
            for key, value in self.properties.items()
            if key.strip()
        }
        if not self.properties:
            raise ValueError("properties must not be empty")
        return self


class UpdateNodePropertiesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str
    updated_properties: dict[str, Any]
    collector_response: dict[str, Any]
    meta: dict[str, Any] = Field(default_factory=dict)

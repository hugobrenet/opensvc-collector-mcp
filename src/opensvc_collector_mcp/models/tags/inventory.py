from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from opensvc_collector_mcp.models.common import ToolConfirmation


def _is_none(value: object) -> bool:
    return value is None


class TagFilterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filters: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Exact-match tag property filters. Keys must be Collector tag "
            "properties returned by list_tag_props."
        ),
        examples=[{"tag_name": "tag_name"}],
    )
    tag_name: str | None = Field(default=None, description="Exact tag name.")
    tag_id: str | None = Field(default=None, description="Exact Collector tag id.")
    tag_exclude: str | None = Field(
        default=None,
        description="Exact Collector tag_exclude value.",
    )

    @model_validator(mode="after")
    def normalize_filters(self) -> "TagFilterRequest":
        self.filters = {
            key.strip(): value.strip()
            for key, value in self.filters.items()
            if key.strip() and value.strip()
        }
        return self

    def merged_filters(self) -> dict[str, str]:
        merged = dict(self.filters)
        for field in ("tag_name", "tag_id", "tag_exclude"):
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


class ListTagsRequest(TagFilterRequest):
    props: str | None = Field(
        default=None,
        description=(
            "Comma-separated tag properties to include in the response. "
            "Defaults to a compact tag inventory view."
        ),
    )
    orderby: str | None = Field(
        default=None,
        description="Collector orderby expression, for example tag_name or ~tag_created.",
    )
    search: str | None = Field(
        default=None,
        description="Collector full-text search expression when supported by /tags.",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=1000,
        description="Maximum number of tags to return.",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of matching tags to skip.",
    )


class CountTagsRequest(TagFilterRequest):
    pass


class CountTagsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    count: int | None
    filters: dict[str, str]


class TagRelationCountResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tag_id: str
    tag_name: str | None = Field(default=None, exclude_if=_is_none)
    tag: dict[str, Any] | None = Field(default=None, exclude_if=_is_none)
    count: int | None
    raw_count: int | None = Field(default=None, exclude_if=_is_none)
    duplicate_count: int | None = Field(default=None, exclude_if=_is_none)
    meta: dict[str, Any] = Field(default_factory=dict)


class TagIdentityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tag_id: str | None = Field(
        default=None,
        description="Exact Collector tag id. Provide either tag_id or tag_name, not both.",
    )
    tag_name: str | None = Field(
        default=None,
        description="Exact tag name to resolve to a Collector tag id. Provide either tag_id or tag_name, not both.",
        examples=["tag_name"],
    )
    @model_validator(mode="after")
    def validate_selector(self) -> "TagIdentityRequest":
        tag_id = self.tag_id.strip() if self.tag_id else None
        tag_name = self.tag_name.strip() if self.tag_name else None
        if bool(tag_id) == bool(tag_name):
            raise ValueError("provide exactly one of tag_id or tag_name")
        self.tag_id = tag_id
        self.tag_name = tag_name
        return self


class TagSelectorRequest(TagIdentityRequest):
    props: str | None = Field(
        default=None,
        description="Comma-separated tag properties to include in the response.",
    )


class TagNodesRequest(TagSelectorRequest):
    props: str | None = Field(
        default=None,
        description="Comma-separated node properties to include in the response.",
    )
    max_nodes: int = Field(
        default=200000,
        ge=1,
        le=500000,
        description="Maximum number of nodes to return from Collector pagination.",
    )


class TagNodesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tag_id: str
    tag_name: str | None = Field(default=None, exclude_if=_is_none)
    tag: dict[str, Any] | None = Field(default=None, exclude_if=_is_none)
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[dict[str, Any]]


class CountTagServicesRequest(TagIdentityRequest):
    max_services: int = Field(
        default=200000,
        ge=1,
        le=500000,
        description="Maximum number of raw service rows to scan for an exact deduplicated count.",
    )


class TagServicesRequest(TagSelectorRequest):
    props: str | None = Field(
        default=None,
        description=(
            "Comma-separated service properties to include in the response. "
            "svcname is always included."
        ),
    )
    max_services: int = Field(
        default=200000,
        ge=1,
        le=500000,
        description="Maximum number of services to return from Collector pagination.",
    )


class TagServicesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tag_id: str
    tag_name: str | None = Field(default=None, exclude_if=_is_none)
    tag: dict[str, Any] | None = Field(default=None, exclude_if=_is_none)
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[dict[str, Any]]


class TagPropsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    count: int = Field(description="Number of tag properties exposed by Collector.")
    available_props: list[str] = Field(
        description="Raw Collector tag properties, including table prefixes."
    )
    tag_props: list[str] = Field(
        description="Tag property names without the tags. table prefix."
    )


class TagRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = Field(
        default=None,
        description="Collector internal tag row id.",
        exclude_if=_is_none,
    )
    tag_id: str | None = Field(
        default=None,
        description="Collector tag id.",
        exclude_if=_is_none,
    )
    tag_name: str | None = Field(
        default=None,
        description="Tag name.",
        exclude_if=_is_none,
    )
    tag_exclude: bool | str | None = Field(
        default=None,
        description="Collector tag exclusion flag/value.",
        exclude_if=_is_none,
    )
    tag_created: str | None = Field(
        default=None,
        description="Tag creation timestamp as exposed by Collector.",
        exclude_if=_is_none,
    )
    tag_data: str | dict[str, Any] | None = Field(
        default=None,
        description="Raw dynamic tag data when returned by Collector.",
        exclude_if=_is_none,
    )


class TagRowsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[TagRow]


class CreateTagRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tag_name: str = Field(
        description="Unique OpenSVC Collector tag name to create.",
        min_length=1,
        examples=["mcp-test-tag"],
    )
    tag_data: str | None = Field(
        default=None,
        description="Optional raw tag data stored by Collector.",
    )
    tag_exclude: str | None = Field(
        default=None,
        description="Optional Collector tag exclusion value.",
    )
    confirmation: ToolConfirmation = Field(
        description=(
            "Required confirmation gate for this state-changing tool. Before "
            "calling create_tag, summarize the exact tag to create, ask the "
            "user to repeat a concise confirmation phrase verbatim, and set this "
            "field only when that exact phrase appears in the latest user message."
        ),
    )

    @model_validator(mode="after")
    def normalize(self) -> "CreateTagRequest":
        self.tag_name = self.tag_name.strip()
        if not self.tag_name:
            raise ValueError("tag_name must not be empty")
        return self


class CreateTagResponse(TagRowsResponse):
    info: str | None = Field(
        default=None,
        description="Collector informational message returned after tag creation.",
        exclude_if=_is_none,
    )


class DeleteTagRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tag_id: str = Field(
        description=(
            "Exact Collector tag id to delete. Use list_tags with props "
            "tag_id,tag_name to resolve tag names before deletion."
        ),
        min_length=1,
        examples=["TAG-ID"],
    )
    confirm_tag_id: str = Field(
        description="Exact tag_id confirmation required before deleting the tag.",
        min_length=1,
        examples=["TAG-ID"],
    )
    confirm_tag_name: str = Field(
        description=(
            "Exact tag_name read from the tag snapshot. This is a human safety "
            "confirmation, not the deletion selector."
        ),
        min_length=1,
        examples=["mcp-test-tag"],
    )
    confirmation: ToolConfirmation = Field(
        description=(
            "Required confirmation gate for this destructive tool. Before calling "
            "delete_tag, generate a concise phrase containing the exact tag_id "
            "and tag_name, ask the user to repeat it verbatim, and set this field "
            "only when that exact phrase appears in the latest user message."
        ),
    )

    @model_validator(mode="after")
    def normalize_confirmation(self) -> "DeleteTagRequest":
        self.tag_id = self.tag_id.strip()
        self.confirm_tag_id = self.confirm_tag_id.strip()
        self.confirm_tag_name = self.confirm_tag_name.strip()
        if not self.tag_id:
            raise ValueError("tag_id must not be empty")
        if not self.confirm_tag_id:
            raise ValueError("confirm_tag_id must not be empty")
        if self.confirm_tag_id != self.tag_id:
            raise ValueError("confirm_tag_id must match tag_id")
        if not self.confirm_tag_name:
            raise ValueError("confirm_tag_name must not be empty")
        return self


class DeleteTagResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tag_id: str
    tag_name: str
    tag: dict[str, Any]
    deleted: bool
    collector_response: dict[str, Any]
    meta: dict[str, Any] = Field(default_factory=dict)

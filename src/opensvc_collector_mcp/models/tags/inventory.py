from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


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


class TagSelectorRequest(BaseModel):
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
    props: str | None = Field(
        default=None,
        description="Comma-separated tag properties to include in the response.",
    )

    @model_validator(mode="after")
    def validate_selector(self) -> "TagSelectorRequest":
        tag_id = self.tag_id.strip() if self.tag_id else None
        tag_name = self.tag_name.strip() if self.tag_name else None
        if bool(tag_id) == bool(tag_name):
            raise ValueError("provide exactly one of tag_id or tag_name")
        self.tag_id = tag_id
        self.tag_name = tag_name
        return self


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

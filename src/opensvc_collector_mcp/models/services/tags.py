from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ._common import ServiceNameRequest, _is_none
from .inventory import ServiceRow


class ServiceTagSearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tag_name: str = Field(
        min_length=1,
        description="Exact OpenSVC Collector tag name.",
        examples=["LAB-TAG"],
    )
    props: str | None = Field(
        default=None,
        description=(
            "Comma-separated service properties to return. svcname is always "
            "included because it is required to identify services."
        ),
    )
    max_services: int = Field(
        default=200000,
        ge=1,
        le=500000,
        description="Maximum number of services the tool may scan or return.",
    )


class ServiceTagsRequest(ServiceNameRequest):
    filters: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Exact-match service tag filters. Keys can be tag_name, tag_id, "
            "tag_exclude, tag_data, or their tags.<field> form."
        ),
        examples=[{"tag_name": "LAB-TAG"}],
    )
    tag_name: str | None = Field(default=None, description="Exact tag name filter.")
    tag_id: str | None = Field(
        default=None, description="Exact Collector tag id filter."
    )
    tag_exclude: str | None = Field(
        default=None, description="Exact tag exclude filter."
    )
    props: str | None = Field(
        default=None,
        description=(
            "Comma-separated tag properties to return. Defaults to a compact "
            "service tag view."
        ),
    )
    max_tags: int = Field(
        default=10000,
        ge=1,
        le=100000,
        description="Maximum number of matching tags the tool may return.",
    )

    @model_validator(mode="after")
    def normalize_filters(self) -> "ServiceTagsRequest":
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


class ServiceTagRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    tag_name: str | None = Field(
        default=None,
        description="Service tag name.",
        exclude_if=_is_none,
    )
    tag_id: str | None = Field(
        default=None,
        description="Collector tag id.",
        exclude_if=_is_none,
    )
    tag_data: str | None = Field(
        default=None,
        description="Tag data payload when returned by Collector.",
        exclude_if=_is_none,
    )
    tag_exclude: str | None = Field(
        default=None,
        description="Tag exclusion flag or expression when returned by Collector.",
        exclude_if=_is_none,
    )
    tag_created: str | None = Field(
        default=None,
        description="Tag creation timestamp.",
        exclude_if=_is_none,
    )


class ServiceTagsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    svcname: str
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ServiceTagRow]


class ServicesByTagResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tag_name: str
    tag_id: str | None = Field(default=None, exclude_if=_is_none)
    tag: ServiceTagRow | None = Field(default=None, exclude_if=_is_none)
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ServiceRow]


class ServicesWithoutTagResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tag_name: str
    tag_id: str | None = Field(default=None, exclude_if=_is_none)
    tag: ServiceTagRow | None = Field(default=None, exclude_if=_is_none)
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ServiceRow]

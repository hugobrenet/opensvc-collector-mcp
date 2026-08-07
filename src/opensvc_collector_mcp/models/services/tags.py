from pydantic import BaseModel, ConfigDict, Field, model_validator

from opensvc_collector_mcp.models.pagination import Pagination

from ._common import ServiceRelationCollectionRequest, _is_none


class ServiceTagsRequest(ServiceRelationCollectionRequest):
    filters: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Exact-match service tag filters. Keys can be tag_name, tag_id, "
            "tag_exclude, tag_data, or their tags.<field> form."
        ),
        examples=[{"tag_name": "tag_name"}],
    )
    tag_name: str | None = Field(default=None, description="Exact tag name filter.")
    tag_id: str | None = Field(
        default=None, description="Exact Collector tag id filter."
    )
    tag_exclude: str | None = Field(
        default=None, description="Exact tag exclude filter."
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
    pagination: Pagination
    data: list[ServiceTagRow]

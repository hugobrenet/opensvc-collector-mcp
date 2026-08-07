from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from opensvc_collector_mcp.models.pagination import Pagination


def _is_none(value: object) -> bool:
    return value is None


class AppFilterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filters: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Exact-match app property filters. Keys must be Collector app "
            "properties returned by list_app_props."
        ),
        examples=[{"app": "APP-CODE"}],
    )
    app: str | None = Field(default=None, description="Exact application code.")
    app_domain: str | None = Field(default=None, description="Exact app domain.")
    app_team_ops: str | None = Field(
        default=None,
        description="Exact app operations team.",
    )

    @model_validator(mode="after")
    def normalize_filters(self) -> "AppFilterRequest":
        self.filters = {
            key.strip(): value.strip()
            for key, value in self.filters.items()
            if key.strip() and value.strip()
        }
        return self

    def merged_filters(self) -> dict[str, str]:
        merged = dict(self.filters)
        for field in ("app", "app_domain", "app_team_ops"):
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


class AppResponsibilityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app: str = Field(
        min_length=1,
        description="Collector app selector. Use an exact app code or Collector app row id.",
        examples=["APP-CODE"],
    )


class AppResponsibilityResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app: str
    responsible: bool
    meta: dict[str, Any] = Field(default_factory=dict)


class GetAppRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app: str = Field(
        min_length=1,
        description="Collector app selector. Use an exact app code or Collector app row id.",
        examples=["APP-CODE"],
    )
    props: str | None = Field(
        default=None,
        description="Comma-separated app properties to include in the response.",
    )


class AppRelationCountRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app: str = Field(
        min_length=1,
        description="Collector app selector. Use an exact app code or Collector app row id.",
        examples=["APP-CODE"],
    )


class AppRelationCountResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app: str
    count: int | None
    meta: dict[str, Any] = Field(default_factory=dict)


class AppNodesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app: str = Field(
        min_length=1,
        description="Collector app selector. Use an exact app code or Collector app row id.",
        examples=["APP-CODE"],
    )
    props: str | None = Field(
        default=None,
        description="Comma-separated node properties to include in the response.",
    )
    filters: dict[str, str] = Field(
        default_factory=dict,
        description="Exact-match node property filters.",
    )
    orderby: str | None = Field(
        default="nodename",
        description="Collector node ordering expression.",
    )
    search: str | None = Field(
        default=None,
        description="Collector full-text node search expression.",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=1000,
        description="Maximum number of attached nodes to return.",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of matching attached nodes to skip.",
    )


class AppNodesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app: str
    pagination: Pagination
    data: list[dict[str, Any]]


class AppGroupRelationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app: str = Field(
        min_length=1,
        description="Collector app selector. Use an exact app code or Collector app row id.",
        examples=["APP-CODE"],
    )
    props: str | None = Field(
        default=None,
        description="Comma-separated group properties to include in the response.",
    )
    filters: dict[str, str] = Field(
        default_factory=dict,
        description="Exact-match group property filters.",
    )
    orderby: str | None = Field(
        default="role",
        description="Collector group ordering expression.",
    )
    search: str | None = Field(
        default=None,
        description="Collector full-text group search expression.",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=1000,
        description="Maximum number of groups to return.",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of matching groups to skip.",
    )


class AppGroupRelationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app: str
    pagination: Pagination
    data: list[dict[str, Any]]


class AppQuotasRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app: str = Field(
        min_length=1,
        description="Collector app selector. Use an exact app code or Collector app row id.",
        examples=["APP-CODE"],
    )
    props: str | None = Field(
        default=None,
        description="Comma-separated quota properties to include in the response.",
    )
    filters: dict[str, str] = Field(
        default_factory=dict,
        description="Exact-match quota property filters.",
    )
    orderby: str | None = Field(
        default="array_name",
        description="Collector quota ordering expression.",
    )
    search: str | None = Field(
        default=None,
        description="Collector full-text quota search expression.",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=1000,
        description="Maximum number of quota rows to return.",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of matching quota rows to skip.",
    )


class AppQuotasResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app: str
    pagination: Pagination
    data: list[dict[str, Any]]


class AppServicesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app: str = Field(
        min_length=1,
        description="Collector app selector. Use an exact app code or Collector app row id.",
        examples=["APP-CODE"],
    )
    props: str | None = Field(
        default=None,
        description="Comma-separated service properties to include in the response.",
    )
    filters: dict[str, str] = Field(
        default_factory=dict,
        description="Exact-match service property filters.",
    )
    orderby: str | None = Field(
        default="svcname",
        description="Collector service ordering expression.",
    )
    search: str | None = Field(
        default=None,
        description="Collector full-text service search expression.",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=1000,
        description="Maximum number of attached services to return.",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of matching attached services to skip.",
    )


class AppServicesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app: str
    pagination: Pagination
    data: list[dict[str, Any]]


class CountAppsRequest(AppFilterRequest):
    search: str | None = Field(
        default=None,
        description="Collector full-text search expression when supported by /apps.",
    )


class CountAppsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    count: int | None
    filters: dict[str, str]
    search: str | None = None


class ListAppsRequest(AppFilterRequest):
    props: str | None = Field(
        default=None,
        description=(
            "Comma-separated app properties to include in the response. "
            "Defaults to a compact app inventory view."
        ),
    )
    orderby: str | None = Field(
        default=None,
        description="Collector orderby expression, for example app or ~updated.",
    )
    search: str | None = Field(
        default=None,
        description="Collector full-text search expression when supported by /apps.",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=1000,
        description="Maximum number of apps to return.",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of matching apps to skip.",
    )


class AppPropsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    count: int = Field(description="Number of app properties exposed by Collector.")
    available_props: list[str] = Field(
        description="Raw Collector app properties, including table prefixes."
    )
    app_props: list[str] = Field(
        description="App property names without the apps. table prefix."
    )


class AppRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = Field(
        default=None,
        description="Collector internal app row id.",
        exclude_if=_is_none,
    )
    app: str | None = Field(
        default=None,
        description="Application code.",
        exclude_if=_is_none,
    )
    app_domain: str | None = Field(
        default=None,
        description="Application domain.",
        exclude_if=_is_none,
    )
    app_team_ops: str | None = Field(
        default=None,
        description="Application operations team.",
        exclude_if=_is_none,
    )
    description: str | None = Field(
        default=None,
        description="Application description.",
        exclude_if=_is_none,
    )
    updated: str | None = Field(
        default=None,
        description="Application update timestamp as exposed by Collector.",
        exclude_if=_is_none,
    )


class AppRowsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[AppRow]


class AppPageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pagination: Pagination
    data: list[AppRow]

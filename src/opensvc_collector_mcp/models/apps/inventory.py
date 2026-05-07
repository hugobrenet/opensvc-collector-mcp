from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


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

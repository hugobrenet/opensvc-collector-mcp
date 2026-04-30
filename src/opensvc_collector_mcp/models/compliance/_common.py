from pydantic import BaseModel, Field, model_validator


class ComplianceListRequest(BaseModel):
    filters: dict[str, str] = Field(
        default_factory=dict,
        description="Exact-match Collector filters. Keys can be raw Collector properties.",
    )
    props: str | None = Field(
        default=None,
        description="Comma-separated Collector properties to return.",
    )
    orderby: str | None = Field(
        default=None,
        description="Collector orderby expression, for example modset_name or ~modset_updated.",
    )
    search: str | None = Field(
        default=None,
        description="Collector full-text search expression when supported by the endpoint.",
    )
    limit: int = Field(default=20, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def normalize_filters(self) -> "ComplianceListRequest":
        self.filters = {
            key.strip(): value.strip()
            for key, value in self.filters.items()
            if key.strip() and value.strip()
        }
        return self

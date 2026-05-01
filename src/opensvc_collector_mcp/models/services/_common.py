from pydantic import BaseModel, ConfigDict, Field, model_validator


def _is_none(value: object) -> bool:
    return value is None


class ServiceNameRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    svcname: str = Field(
        min_length=1,
        description="Exact OpenSVC Collector service name.",
        examples=["tst-lab-service"],
    )

class ServiceRelationCollectionRequest(ServiceNameRequest):
    filters: dict[str, str] = Field(
        default_factory=dict,
        description="Exact-match Collector filters for this service relation endpoint.",
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
    def normalize_filters(self) -> "ServiceRelationCollectionRequest":
        self.filters = {
            key.strip(): value.strip()
            for key, value in self.filters.items()
            if key.strip() and value.strip()
        }
        return self

    def merged_filters(self) -> dict[str, str]:
        return dict(self.filters)

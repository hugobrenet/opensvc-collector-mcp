from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


def _is_none(value: object) -> bool:
    return value is None


class ArrayFilterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filters: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Exact-match array property filters. Keys must be Collector array "
            "properties returned by list_array_props."
        ),
        examples=[{"array_name": "ARRAY-NAME"}],
    )
    array_name: str | None = Field(default=None, description="Exact storage array name.")
    array_model: str | None = Field(default=None, description="Exact storage array model.")
    array_level: str | None = Field(default=None, description="Exact storage array level.")

    @model_validator(mode="after")
    def normalize_filters(self) -> "ArrayFilterRequest":
        self.filters = {
            key.strip(): value.strip()
            for key, value in self.filters.items()
            if key.strip() and value.strip()
        }
        return self

    def merged_filters(self) -> dict[str, str]:
        merged = dict(self.filters)
        for field in ("array_name", "array_model", "array_level"):
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


class GetArrayRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    array: str = Field(
        min_length=1,
        description=(
            "Collector array selector. Use an exact storage array name "
            "or Collector array row id."
        ),
        examples=["ARRAY-NAME"],
    )
    props: str | None = Field(
        default=None,
        description="Comma-separated array properties to include in the response.",
    )


class CountArraysRequest(ArrayFilterRequest):
    search: str | None = Field(
        default=None,
        description="Collector full-text search expression when supported by /arrays.",
    )


class CountArraysResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    count: int | None
    filters: dict[str, str] = Field(default_factory=dict)
    search: str | None = None


class ListArraysRequest(ArrayFilterRequest):
    props: str | None = Field(
        default=None,
        description=(
            "Comma-separated array properties to include in the response. "
            "Defaults to a compact array inventory view."
        ),
    )
    orderby: str | None = Field(
        default=None,
        description="Collector orderby expression, for example array_name or ~array_updated.",
    )
    search: str | None = Field(
        default=None,
        description="Collector full-text search expression when supported by /arrays.",
    )
    limit: int = Field(default=20, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class ArrayPropsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    count: int = Field(description="Number of array properties exposed by Collector.")
    available_props: list[str] = Field(
        description="Raw Collector array properties, including table prefixes."
    )
    array_props: list[str] = Field(
        description="Array property names without the stor_array. table prefix."
    )


class ArrayRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = Field(default=None, exclude_if=_is_none)
    array_name: str | None = Field(default=None, exclude_if=_is_none)
    array_model: str | None = Field(default=None, exclude_if=_is_none)
    array_firmware: str | None = Field(default=None, exclude_if=_is_none)
    array_cache: int | str | None = Field(default=None, exclude_if=_is_none)
    array_level: int | str | None = Field(default=None, exclude_if=_is_none)
    array_comment: str | None = Field(default=None, exclude_if=_is_none)
    array_updated: str | None = Field(default=None, exclude_if=_is_none)


class ArrayRowsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ArrayRow]

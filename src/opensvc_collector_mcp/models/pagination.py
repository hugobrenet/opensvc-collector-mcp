from pydantic import BaseModel, ConfigDict, Field


class Pagination(BaseModel):
    """Stable pagination contract exposed by raw collection tools."""

    model_config = ConfigDict(extra="forbid")

    limit: int = Field(description="Maximum number of rows requested for this page.")
    offset: int = Field(description="Number of matching rows skipped before this page.")
    returned: int = Field(description="Number of rows returned in this page.")
    next_offset: int | None = Field(
        description=(
            "Offset to use for the next call, or null when this page proves that "
            "the collection is complete."
        ),
    )
    complete: bool = Field(
        description=(
            "True when fewer rows than the requested limit were returned. A full "
            "page remains incomplete until a later short or empty page is read."
        ),
    )
    truncated: bool = Field(
        default=False,
        description=(
            "True when a bounded server-side scan stopped before exhausting its "
            "source. Raw one-page collection calls always return false."
        ),
    )

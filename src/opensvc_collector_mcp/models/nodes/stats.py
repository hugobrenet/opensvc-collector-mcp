from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class InventoryStatsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fields: str | None = Field(
        default=None,
        description=(
            "Comma-separated node properties to aggregate. Defaults to status, "
            "asset_env, node_env, loc_city, loc_country, app, and os_name."
        ),
    )
    page_size: int = Field(
        default=1000,
        ge=1,
        le=5000,
        description="Number of nodes fetched per Collector request.",
    )
    max_nodes: int = Field(
        default=200000,
        ge=1,
        le=500000,
        description="Maximum number of nodes to scan before returning partial stats.",
    )


class InventoryStatsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meta: dict[str, Any]
    stats: dict[str, dict[str, int]]

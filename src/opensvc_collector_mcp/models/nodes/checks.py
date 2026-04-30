from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class NodeCheckEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    svc_id: str | None = None
    chk_created: str | None = None
    chk_updated: str | None = None
    chk_type: str | None = None
    chk_instance: str | None = None
    chk_value: Any = None
    chk_threshold_provider: str | None = None
    chk_err: int | None = None
    chk_high: Any = None
    chk_low: Any = None
    id: int | None = None
    node_id: str | None = None


class NodeChecksResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[NodeCheckEntry]

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class NodeLocation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    country: str | None = None
    city: str | None = None
    building: str | None = None
    room: str | None = None
    floor: str | None = None
    rack: str | None = None
    enclosure: str | None = None
    enclosure_slot: str | None = None
    address: str | None = None
    zip: str | None = None


class NodeLocationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str
    location: NodeLocation
    raw: dict[str, Any] = Field(default_factory=dict)

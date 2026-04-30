from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class NodeOperatingSystem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    vendor: str | None = None
    release: str | None = None
    kernel: str | None = None
    arch: str | None = None
    concat: str | None = None


class NodeOsRuntime(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str | None = None
    service_pack: str | None = None
    timezone: str | None = None
    last_boot: str | None = None


class NodeOsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str
    os: NodeOperatingSystem
    runtime: NodeOsRuntime
    raw: dict[str, Any] = Field(default_factory=dict)

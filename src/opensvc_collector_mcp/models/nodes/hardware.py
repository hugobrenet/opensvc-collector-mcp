from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class NodeHardwareIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    serial: str | None = None
    bios_version: str | None = None


class NodeCpuHardware(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str | None = None
    vendor: str | None = None
    cores: int | None = None
    threads: int | None = None
    dies: int | None = None
    frequency: int | None = None


class NodeMemoryHardware(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bytes: int | None = None
    banks: int | None = None
    slots: int | None = None


class NodePowerHardware(BaseModel):
    model_config = ConfigDict(extra="forbid")

    supply_count: int | None = None
    cabinet1: str | None = None
    cabinet2: str | None = None
    breaker1: str | None = None
    breaker2: str | None = None
    protect: str | None = None
    protect_breaker: str | None = None


class NodeHardwarePlacement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enclosure: str | None = None
    enclosure_slot: str | None = None


class NodeHardwareResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str
    hardware: NodeHardwareIdentity
    cpu: NodeCpuHardware
    memory: NodeMemoryHardware
    power: NodePowerHardware
    placement: NodeHardwarePlacement
    raw: dict[str, Any] = Field(default_factory=dict)

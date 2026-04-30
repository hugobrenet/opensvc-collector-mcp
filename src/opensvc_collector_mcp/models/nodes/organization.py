from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class NodeOrganization(BaseModel):
    model_config = ConfigDict(extra="forbid")

    responsible: str | None = None
    integration: str | None = None
    support: str | None = None
    app: str | None = None


class NodeOrganizationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str
    organization: NodeOrganization
    raw: dict[str, Any] = Field(default_factory=dict)

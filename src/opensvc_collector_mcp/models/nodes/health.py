from typing import Any

from pydantic import BaseModel, ConfigDict


class NodeHealthIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    severity: str
    field: str
    message: str


class NodeHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    overall: str
    severity: str
    node: dict[str, Any]
    issues: list[NodeHealthIssue]
    signals: dict[str, Any]

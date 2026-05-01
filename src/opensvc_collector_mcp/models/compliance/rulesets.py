from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ._common import ComplianceListRequest


class ComplianceRulesetsRequest(ComplianceListRequest):
    orderby: str | None = Field(
        default="ruleset_name",
        description="Collector orderby expression. Defaults to ruleset_name.",
    )


class ComplianceRulesetRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | str | None = Field(default=None, description="Collector ruleset id.")
    ruleset_name: str | None = Field(
        default=None, description="Compliance ruleset name."
    )
    ruleset_type: str | None = Field(
        default=None, description="Compliance ruleset type."
    )
    ruleset_public: bool | None = Field(
        default=None,
        description="Whether the compliance ruleset is public.",
    )


class ComplianceRulesetsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ComplianceRulesetRow]

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ._common import ComplianceListRequest


class ComplianceModulesetsRequest(ComplianceListRequest):
    orderby: str | None = Field(
        default="modset_name",
        description="Collector orderby expression. Defaults to modset_name.",
    )


class ComplianceModulesetRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | str | None = Field(default=None, description="Collector moduleset id.")
    modset_name: str | None = Field(default=None, description="Compliance moduleset name.")
    modset_author: str | None = Field(default=None, description="Moduleset author.")
    modset_updated: str | None = Field(default=None, description="Moduleset update timestamp.")


class ComplianceModulesetsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ComplianceModulesetRow]

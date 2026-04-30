from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ._common import ComplianceListRequest


class ComplianceModulesetsRequest(ComplianceListRequest):
    orderby: str | None = Field(
        default="modset_name",
        description="Collector orderby expression. Defaults to modset_name.",
    )


class ComplianceModulesetRequest(BaseModel):
    moduleset_id: int | str | None = Field(
        default=None,
        description="Collector compliance moduleset id, when already known.",
    )
    modset_name: str | None = Field(
        default=None,
        description="Exact compliance moduleset name to resolve to a Collector id.",
        examples=["01-aits.nodes.opensvc"],
    )
    props: str | None = Field(
        default=None,
        description="Comma-separated moduleset properties to return.",
    )

    @model_validator(mode="after")
    def require_selector(self) -> "ComplianceModulesetRequest":
        has_id = self.moduleset_id is not None and str(self.moduleset_id).strip()
        has_name = self.modset_name is not None and self.modset_name.strip()
        if not has_id and not has_name:
            raise ValueError("moduleset_id or modset_name must be provided")
        if self.modset_name is not None:
            self.modset_name = self.modset_name.strip() or None
        return self


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



class ComplianceModulesetResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_id: str
    modset_name: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ComplianceModulesetRow]

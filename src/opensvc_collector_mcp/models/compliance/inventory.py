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


class ComplianceModulesetDefinitionRequest(BaseModel):
    moduleset_id: int | str | None = Field(
        default=None,
        description="Collector compliance moduleset id, when already known.",
    )
    modset_name: str | None = Field(
        default=None,
        description="Exact compliance moduleset name to resolve to a Collector id.",
        examples=["02-aits.nodes.opensvc.tags"],
    )
    include_variable_values: bool = Field(
        default=False,
        description=(
            "Include ruleset variable values from the export payload. Disabled "
            "by default because values can be large or sensitive."
        ),
    )

    @model_validator(mode="after")
    def require_selector(self) -> "ComplianceModulesetDefinitionRequest":
        has_id = self.moduleset_id is not None and str(self.moduleset_id).strip()
        has_name = self.modset_name is not None and self.modset_name.strip()
        if not has_id and not has_name:
            raise ValueError("moduleset_id or modset_name must be provided")
        if self.modset_name is not None:
            self.modset_name = self.modset_name.strip() or None
        return self


class ComplianceModulesetUsageRequest(BaseModel):
    moduleset_id: int | str | None = Field(
        default=None,
        description="Collector compliance moduleset id, when already known.",
    )
    modset_name: str | None = Field(
        default=None,
        description="Exact compliance moduleset name to resolve to a Collector id.",
        examples=["02-aits.nodes.opensvc.tags"],
    )

    @model_validator(mode="after")
    def require_selector(self) -> "ComplianceModulesetUsageRequest":
        has_id = self.moduleset_id is not None and str(self.moduleset_id).strip()
        has_name = self.modset_name is not None and self.modset_name.strip()
        if not has_id and not has_name:
            raise ValueError("moduleset_id or modset_name must be provided")
        if self.modset_name is not None:
            self.modset_name = self.modset_name.strip() or None
        return self


class ComplianceModulesetRelationRequest(ComplianceListRequest):
    moduleset_id: int | str | None = Field(
        default=None,
        description="Collector compliance moduleset id, when already known.",
    )
    modset_name: str | None = Field(
        default=None,
        description="Exact compliance moduleset name to resolve to a Collector id.",
        examples=["02-aits.nodes.opensvc.tags"],
    )

    @model_validator(mode="after")
    def require_selector(self) -> "ComplianceModulesetRelationRequest":
        super().normalize_filters()
        has_id = self.moduleset_id is not None and str(self.moduleset_id).strip()
        has_name = self.modset_name is not None and self.modset_name.strip()
        if not has_id and not has_name:
            raise ValueError("moduleset_id or modset_name must be provided")
        if self.modset_name is not None:
            self.modset_name = self.modset_name.strip() or None
        return self


class ComplianceModulesetModulesRequest(ComplianceModulesetRelationRequest):
    orderby: str | None = Field(
        default="modset_mod_name",
        description="Collector orderby expression. Defaults to modset_mod_name.",
    )


class ComplianceModulesetNodesRequest(ComplianceModulesetRelationRequest):
    orderby: str | None = Field(
        default="nodename",
        description="Collector orderby expression. Defaults to nodename.",
    )


class ComplianceModulesetCandidateNodesRequest(ComplianceModulesetRelationRequest):
    orderby: str | None = Field(
        default="nodename",
        description="Collector orderby expression. Defaults to nodename.",
    )


class ComplianceModulesetServicesRequest(ComplianceModulesetRelationRequest):
    orderby: str | None = Field(
        default="svcname",
        description="Collector orderby expression. Defaults to svcname.",
    )


class ComplianceModulesetCandidateServicesRequest(ComplianceModulesetRelationRequest):
    orderby: str | None = Field(
        default="svcname",
        description="Collector orderby expression. Defaults to svcname.",
    )


class ComplianceModulesetPublicationsRequest(ComplianceModulesetRelationRequest):
    orderby: str | None = Field(
        default="role",
        description="Collector orderby expression. Defaults to role.",
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



class ComplianceModulesetResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_id: str
    modset_name: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ComplianceModulesetRow]



class ComplianceModulesetDefinitionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_id: str
    modset_name: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
    definition: dict[str, Any] = Field(default_factory=dict)


class ComplianceModulesetUsageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_id: str
    modset_name: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
    data: dict[str, Any] = Field(default_factory=dict)


class ComplianceModulesetModuleRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | str | None = Field(default=None, description="Collector module row id.")
    modset_id: int | str | None = Field(default=None, description="Collector moduleset id.")
    modset_mod_name: str | None = Field(default=None, description="Moduleset module name.")
    autofix: bool | None = Field(default=None, description="Whether the module supports autofix.")
    modset_mod_author: str | None = Field(default=None, description="Module author.")
    modset_mod_updated: str | None = Field(default=None, description="Module update timestamp.")


class ComplianceModulesetModulesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_id: str
    modset_name: str | None = None
    relation: str = Field(default="modules")
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ComplianceModulesetModuleRow]


class ComplianceModulesetNodeRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    node_id: str | None = Field(default=None, description="Collector node id.")
    nodename: str | None = Field(default=None, description="OpenSVC node name.")
    app: str | None = Field(default=None, description="Node application.")
    node_env: str | None = Field(default=None, description="Node environment.")
    status: str | None = Field(default=None, description="Node status.")
    updated: str | None = Field(default=None, description="Node update timestamp.")


class ComplianceModulesetNodesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_id: str
    modset_name: str | None = None
    relation: str = Field(default="nodes")
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ComplianceModulesetNodeRow]


class ComplianceModulesetCandidateNodesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_id: str
    modset_name: str | None = None
    relation: str = Field(default="candidate_nodes")
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ComplianceModulesetNodeRow]


class ComplianceModulesetServiceRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    svc_id: str | None = Field(default=None, description="Collector service id.")
    svcname: str | None = Field(default=None, description="OpenSVC service name.")
    svc_app: str | None = Field(default=None, description="Service application.")
    svc_env: str | None = Field(default=None, description="Service environment.")
    svc_status: str | None = Field(default=None, description="Service status.")
    svc_availstatus: str | None = Field(default=None, description="Service availability status.")
    updated: str | None = Field(default=None, description="Service update timestamp.")


class ComplianceModulesetServicesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_id: str
    modset_name: str | None = None
    relation: str = Field(default="services")
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ComplianceModulesetServiceRow]


class ComplianceModulesetCandidateServicesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_id: str
    modset_name: str | None = None
    relation: str = Field(default="candidate_services")
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ComplianceModulesetServiceRow]


class ComplianceModulesetGroupRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | str | None = Field(default=None, description="Collector group id.")
    role: str | None = Field(default=None, description="Collector group role/name.")
    description: str | None = Field(default=None, description="Collector group description.")
    privilege: bool | None = Field(default=None, description="Whether the group is privileged.")


class ComplianceModulesetPublicationsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_id: str
    modset_name: str | None = None
    relation: str = Field(default="publications")
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ComplianceModulesetGroupRow]

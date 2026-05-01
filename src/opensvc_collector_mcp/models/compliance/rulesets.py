from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ._common import ComplianceListRequest


class ComplianceRulesetsRequest(ComplianceListRequest):
    orderby: str | None = Field(
        default="ruleset_name",
        description="Collector orderby expression. Defaults to ruleset_name.",
    )


class ComplianceRulesetRequest(BaseModel):
    ruleset_id: int | str | None = Field(
        default=None,
        description="Collector compliance ruleset id, when already known.",
    )
    ruleset_name: str | None = Field(
        default=None,
        description="Exact compliance ruleset name to resolve to a Collector id.",
        examples=["02-aits.nodes.opensvc.tags"],
    )
    props: str | None = Field(
        default=None,
        description="Comma-separated ruleset properties to return.",
    )

    @model_validator(mode="after")
    def require_selector(self) -> "ComplianceRulesetRequest":
        has_id = self.ruleset_id is not None and str(self.ruleset_id).strip()
        has_name = self.ruleset_name is not None and self.ruleset_name.strip()
        if not has_id and not has_name:
            raise ValueError("ruleset_id or ruleset_name must be provided")
        if self.ruleset_name is not None:
            self.ruleset_name = self.ruleset_name.strip() or None
        return self


class ComplianceRulesetUsageRequest(BaseModel):
    ruleset_id: int | str | None = Field(
        default=None,
        description="Collector compliance ruleset id, when already known.",
    )
    ruleset_name: str | None = Field(
        default=None,
        description="Exact compliance ruleset name to resolve to a Collector id.",
        examples=["02-aits.nodes.opensvc.tags"],
    )

    @model_validator(mode="after")
    def require_selector(self) -> "ComplianceRulesetUsageRequest":
        has_id = self.ruleset_id is not None and str(self.ruleset_id).strip()
        has_name = self.ruleset_name is not None and self.ruleset_name.strip()
        if not has_id and not has_name:
            raise ValueError("ruleset_id or ruleset_name must be provided")
        if self.ruleset_name is not None:
            self.ruleset_name = self.ruleset_name.strip() or None
        return self


class ComplianceRulesetVariablesRequest(ComplianceListRequest):
    ruleset_id: int | str | None = Field(
        default=None,
        description="Collector compliance ruleset id, when already known.",
    )
    ruleset_name: str | None = Field(
        default=None,
        description="Exact compliance ruleset name to resolve to a Collector id.",
        examples=["02-aits.nodes.opensvc.tags"],
    )
    orderby: str | None = Field(
        default="var_name",
        description="Collector orderby expression. Defaults to var_name.",
    )
    include_var_value: bool = Field(
        default=False,
        description=(
            "Include ruleset variable values in the response. Disabled by default "
            "because values can be large or sensitive."
        ),
    )

    @model_validator(mode="after")
    def require_selector(self) -> "ComplianceRulesetVariablesRequest":
        has_id = self.ruleset_id is not None and str(self.ruleset_id).strip()
        has_name = self.ruleset_name is not None and self.ruleset_name.strip()
        if not has_id and not has_name:
            raise ValueError("ruleset_id or ruleset_name must be provided")
        if self.ruleset_name is not None:
            self.ruleset_name = self.ruleset_name.strip() or None
        return self


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


class ComplianceRulesetCandidateNodesRequest(ComplianceListRequest):
    ruleset_id: int | str | None = Field(
        default=None,
        description="Collector compliance ruleset id, when already known.",
    )
    ruleset_name: str | None = Field(
        default=None,
        description="Exact compliance ruleset name to resolve to a Collector id.",
        examples=["02-aits.nodes.opensvc.tags"],
    )
    orderby: str | None = Field(
        default="nodename",
        description="Collector orderby expression. Defaults to nodename.",
    )

    @model_validator(mode="after")
    def require_selector(self) -> "ComplianceRulesetCandidateNodesRequest":
        super().normalize_filters()
        has_id = self.ruleset_id is not None and str(self.ruleset_id).strip()
        has_name = self.ruleset_name is not None and self.ruleset_name.strip()
        if not has_id and not has_name:
            raise ValueError("ruleset_id or ruleset_name must be provided")
        if self.ruleset_name is not None:
            self.ruleset_name = self.ruleset_name.strip() or None
        return self


class ComplianceRulesetCandidateServicesRequest(ComplianceListRequest):
    ruleset_id: int | str | None = Field(
        default=None,
        description="Collector compliance ruleset id, when already known.",
    )
    ruleset_name: str | None = Field(
        default=None,
        description="Exact compliance ruleset name to resolve to a Collector id.",
        examples=["02-aits.nodes.opensvc.tags"],
    )
    orderby: str | None = Field(
        default="svcname",
        description="Collector orderby expression. Defaults to svcname.",
    )

    @model_validator(mode="after")
    def require_selector(self) -> "ComplianceRulesetCandidateServicesRequest":
        super().normalize_filters()
        has_id = self.ruleset_id is not None and str(self.ruleset_id).strip()
        has_name = self.ruleset_name is not None and self.ruleset_name.strip()
        if not has_id and not has_name:
            raise ValueError("ruleset_id or ruleset_name must be provided")
        if self.ruleset_name is not None:
            self.ruleset_name = self.ruleset_name.strip() or None
        return self


class ComplianceRulesetPublicationsRequest(ComplianceListRequest):
    ruleset_id: int | str | None = Field(
        default=None,
        description="Collector compliance ruleset id, when already known.",
    )
    ruleset_name: str | None = Field(
        default=None,
        description="Exact compliance ruleset name to resolve to a Collector id.",
        examples=["02-aits.nodes.opensvc.tags"],
    )
    orderby: str | None = Field(
        default="role",
        description="Collector orderby expression. Defaults to role.",
    )

    @model_validator(mode="after")
    def require_selector(self) -> "ComplianceRulesetPublicationsRequest":
        super().normalize_filters()
        has_id = self.ruleset_id is not None and str(self.ruleset_id).strip()
        has_name = self.ruleset_name is not None and self.ruleset_name.strip()
        if not has_id and not has_name:
            raise ValueError("ruleset_id or ruleset_name must be provided")
        if self.ruleset_name is not None:
            self.ruleset_name = self.ruleset_name.strip() or None
        return self


class ComplianceRulesetResponsiblesRequest(ComplianceRulesetPublicationsRequest):
    pass


class ComplianceRulesetVariableRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | str | None = Field(default=None, description="Collector variable row id.")
    ruleset_id: int | str | None = Field(default=None, description="Collector ruleset id.")
    var_name: str | None = Field(default=None, description="Ruleset variable name.")
    var_class: str | None = Field(default=None, description="Ruleset variable class.")
    var_author: str | None = Field(default=None, description="Ruleset variable author.")
    var_updated: str | None = Field(default=None, description="Ruleset variable update timestamp.")
    var_value: Any | None = Field(default=None, description="Ruleset variable value, when requested.")


class ComplianceRulesetsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ComplianceRulesetRow]


class ComplianceRulesetResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_id: str
    ruleset_name: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ComplianceRulesetRow]


class ComplianceRulesetUsageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_id: str
    ruleset_name: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
    data: dict[str, Any] = Field(default_factory=dict)


class ComplianceRulesetNodeRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    node_id: str | None = Field(default=None, description="Collector node id.")
    nodename: str | None = Field(default=None, description="OpenSVC node name.")
    app: str | None = Field(default=None, description="Node application.")
    node_env: str | None = Field(default=None, description="Node environment.")
    status: str | None = Field(default=None, description="Node status.")
    updated: str | None = Field(default=None, description="Node update timestamp.")


class ComplianceRulesetCandidateNodesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_id: str
    relation: str = Field(default="candidate_nodes")
    ruleset_name: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ComplianceRulesetNodeRow]


class ComplianceRulesetServiceRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    svc_id: str | None = Field(default=None, description="Collector service id.")
    svcname: str | None = Field(default=None, description="OpenSVC service name.")
    svc_app: str | None = Field(default=None, description="Service application.")
    svc_env: str | None = Field(default=None, description="Service environment.")
    svc_status: str | None = Field(default=None, description="Service status.")
    svc_availstatus: str | None = Field(default=None, description="Service availability status.")
    updated: str | None = Field(default=None, description="Service update timestamp.")


class ComplianceRulesetCandidateServicesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_id: str
    relation: str = Field(default="candidate_services")
    ruleset_name: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ComplianceRulesetServiceRow]


class ComplianceRulesetGroupRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | str | None = Field(default=None, description="Collector group id.")
    role: str | None = Field(default=None, description="Collector group role name.")
    privilege: bool | None = Field(default=None, description="Whether the group has privilege.")
    description: str | None = Field(default=None, description="Collector group description.")


class ComplianceRulesetPublicationsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_id: str
    relation: str = Field(default="publications")
    ruleset_name: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ComplianceRulesetGroupRow]


class ComplianceRulesetResponsiblesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_id: str
    relation: str = Field(default="responsibles")
    ruleset_name: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ComplianceRulesetGroupRow]


class ComplianceRulesetVariablesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_id: str
    relation: str
    ruleset_name: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[ComplianceRulesetVariableRow]

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from opensvc_collector_mcp.config import TOOL_TIMEOUT_SECONDS
from opensvc_collector_mcp.core.compliance import (
    get_compliance_moduleset as core_get_compliance_moduleset,
    get_compliance_moduleset_definition as core_get_compliance_moduleset_definition,
    list_compliance_modulesets as core_list_compliance_modulesets,
)
from opensvc_collector_mcp.models.compliance import (
    ComplianceModulesetDefinitionRequest,
    ComplianceModulesetDefinitionResponse,
    ComplianceModulesetRequest,
    ComplianceModulesetResponse,
    ComplianceModulesetsRequest,
    ComplianceModulesetsResponse,
)


def register_compliance_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="list_compliance_modulesets",
        description=(
            "List OpenSVC Collector compliance modulesets published to the "
            "requesting user's groups. Use filters for exact-match Collector "
            "filters and props to choose returned moduleset fields."
        ),
        tags={"compliance", "modulesets", "inventory", "read"},
        annotations={
            "title": "List OpenSVC Compliance Modulesets",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def list_compliance_modulesets(
        request: Annotated[
            ComplianceModulesetsRequest,
            Field(
                description=(
                    "Compliance moduleset listing parameters: exact-match filters, "
                    "returned properties, ordering, search, limit, and offset."
                ),
            ),
        ] = ComplianceModulesetsRequest(),
    ) -> ComplianceModulesetsResponse:
        """Return compliance modulesets visible to the Collector account."""
        response = await core_list_compliance_modulesets(
            filters=request.filters,
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            limit=request.limit,
            offset=request.offset,
        )
        return ComplianceModulesetsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_compliance_moduleset",
        description=(
            "Return one OpenSVC Collector compliance moduleset selected by "
            "Collector moduleset id or exact moduleset name. Use "
            "list_compliance_modulesets first when the exact name is unknown."
        ),
        tags={"compliance", "modulesets", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Compliance Moduleset",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_compliance_moduleset(
        request: Annotated[
            ComplianceModulesetRequest,
            Field(
                description=(
                    "Collector moduleset id or exact modset_name plus optional "
                    "returned properties used to retrieve one compliance moduleset."
                ),
            ),
        ],
    ) -> ComplianceModulesetResponse:
        """Return one compliance moduleset visible to the Collector account."""
        response = await core_get_compliance_moduleset(
            moduleset_id=request.moduleset_id,
            modset_name=request.modset_name,
            props=request.props,
        )
        return ComplianceModulesetResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_compliance_moduleset_definition",
        description=(
            "Return the declarative definition/export of one OpenSVC compliance "
            "moduleset selected by id or exact name: modules, rulesets, variables, "
            "filtersets, publications, responsibles, and dependencies. Variable "
            "values are hidden by default."
        ),
        tags={"compliance", "modulesets", "definition", "read"},
        annotations={
            "title": "Get OpenSVC Compliance Moduleset Definition",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_compliance_moduleset_definition(
        request: Annotated[
            ComplianceModulesetDefinitionRequest,
            Field(
                description=(
                    "Collector moduleset id or exact modset_name, plus a flag "
                    "controlling whether ruleset variable values are included."
                ),
            ),
        ],
    ) -> ComplianceModulesetDefinitionResponse:
        """Return the declarative export of one compliance moduleset."""
        response = await core_get_compliance_moduleset_definition(
            moduleset_id=request.moduleset_id,
            modset_name=request.modset_name,
            include_variable_values=request.include_variable_values,
        )
        return ComplianceModulesetDefinitionResponse.model_validate(response)

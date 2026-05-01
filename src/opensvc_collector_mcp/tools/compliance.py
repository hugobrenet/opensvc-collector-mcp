from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from opensvc_collector_mcp.config import TOOL_TIMEOUT_SECONDS
from opensvc_collector_mcp.core.compliance import (
    get_compliance_moduleset as core_get_compliance_moduleset,
    get_compliance_moduleset_candidate_nodes as core_get_compliance_moduleset_candidate_nodes,
    get_compliance_moduleset_candidate_services as core_get_compliance_moduleset_candidate_services,
    get_compliance_moduleset_definition as core_get_compliance_moduleset_definition,
    get_compliance_moduleset_modules as core_get_compliance_moduleset_modules,
    get_compliance_moduleset_nodes as core_get_compliance_moduleset_nodes,
    get_compliance_moduleset_publications as core_get_compliance_moduleset_publications,
    get_compliance_moduleset_responsibles as core_get_compliance_moduleset_responsibles,
    get_compliance_moduleset_services as core_get_compliance_moduleset_services,
    get_compliance_moduleset_usage as core_get_compliance_moduleset_usage,
    list_compliance_modulesets as core_list_compliance_modulesets,
)
from opensvc_collector_mcp.models.compliance import (
    ComplianceModulesetCandidateNodesRequest,
    ComplianceModulesetCandidateNodesResponse,
    ComplianceModulesetCandidateServicesRequest,
    ComplianceModulesetCandidateServicesResponse,
    ComplianceModulesetDefinitionRequest,
    ComplianceModulesetDefinitionResponse,
    ComplianceModulesetModulesRequest,
    ComplianceModulesetModulesResponse,
    ComplianceModulesetNodesRequest,
    ComplianceModulesetNodesResponse,
    ComplianceModulesetPublicationsRequest,
    ComplianceModulesetPublicationsResponse,
    ComplianceModulesetRequest,
    ComplianceModulesetResponsiblesRequest,
    ComplianceModulesetResponsiblesResponse,
    ComplianceModulesetResponse,
    ComplianceModulesetServicesRequest,
    ComplianceModulesetServicesResponse,
    ComplianceModulesetUsageRequest,
    ComplianceModulesetUsageResponse,
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
        name="get_compliance_moduleset_modules",
        description=(
            "Return modules declared in one OpenSVC Collector compliance moduleset, "
            "selected by Collector moduleset id or exact moduleset name. Use this "
            "to inspect the concrete modules composing a moduleset."
        ),
        tags={"compliance", "modulesets", "modules", "read"},
        annotations={
            "title": "Get OpenSVC Compliance Moduleset Modules",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_compliance_moduleset_modules(
        request: Annotated[
            ComplianceModulesetModulesRequest,
            Field(
                description=(
                    "Collector moduleset id or exact modset_name plus optional "
                    "filters, properties, ordering, search, limit, and offset."
                ),
            ),
        ],
    ) -> ComplianceModulesetModulesResponse:
        """Return modules declared in one compliance moduleset."""
        response = await core_get_compliance_moduleset_modules(
            moduleset_id=request.moduleset_id,
            modset_name=request.modset_name,
            filters=request.filters,
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            limit=request.limit,
            offset=request.offset,
        )
        return ComplianceModulesetModulesResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_compliance_moduleset_nodes",
        description=(
            "Return nodes directly attached to one OpenSVC Collector compliance "
            "moduleset, selected by Collector moduleset id or exact moduleset "
            "name. This does not return candidate or merely eligible nodes."
        ),
        tags={"compliance", "modulesets", "nodes", "read"},
        annotations={
            "title": "Get OpenSVC Compliance Moduleset Nodes",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_compliance_moduleset_nodes(
        request: Annotated[
            ComplianceModulesetNodesRequest,
            Field(
                description=(
                    "Collector moduleset id or exact modset_name plus optional "
                    "filters, properties, ordering, search, limit, and offset. "
                    "Returns directly attached nodes only."
                ),
            ),
        ],
    ) -> ComplianceModulesetNodesResponse:
        """Return nodes directly attached to one compliance moduleset."""
        response = await core_get_compliance_moduleset_nodes(
            moduleset_id=request.moduleset_id,
            modset_name=request.modset_name,
            filters=request.filters,
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            limit=request.limit,
            offset=request.offset,
        )
        return ComplianceModulesetNodesResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_compliance_moduleset_services",
        description=(
            "Return services directly attached to one OpenSVC Collector compliance "
            "moduleset, selected by Collector moduleset id or exact moduleset "
            "name. This does not return candidate or merely eligible services."
        ),
        tags={"compliance", "modulesets", "services", "read"},
        annotations={
            "title": "Get OpenSVC Compliance Moduleset Services",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_compliance_moduleset_services(
        request: Annotated[
            ComplianceModulesetServicesRequest,
            Field(
                description=(
                    "Collector moduleset id or exact modset_name plus optional "
                    "filters, properties, ordering, search, limit, and offset. "
                    "Returns directly attached services only."
                ),
            ),
        ],
    ) -> ComplianceModulesetServicesResponse:
        """Return services directly attached to one compliance moduleset."""
        response = await core_get_compliance_moduleset_services(
            moduleset_id=request.moduleset_id,
            modset_name=request.modset_name,
            filters=request.filters,
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            limit=request.limit,
            offset=request.offset,
        )
        return ComplianceModulesetServicesResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_compliance_moduleset_publications",
        description=(
            "Return groups one OpenSVC Collector compliance moduleset is published "
            "to, selected by Collector moduleset id or exact moduleset name. Use "
            "this to know which groups can see or use a moduleset."
        ),
        tags={"compliance", "modulesets", "groups", "publications", "read"},
        annotations={
            "title": "Get OpenSVC Compliance Moduleset Publications",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_compliance_moduleset_publications(
        request: Annotated[
            ComplianceModulesetPublicationsRequest,
            Field(
                description=(
                    "Collector moduleset id or exact modset_name plus optional "
                    "filters, properties, ordering, search, limit, and offset. "
                    "Returns groups the moduleset is published to."
                ),
            ),
        ],
    ) -> ComplianceModulesetPublicationsResponse:
        """Return groups one compliance moduleset is published to."""
        response = await core_get_compliance_moduleset_publications(
            moduleset_id=request.moduleset_id,
            modset_name=request.modset_name,
            filters=request.filters,
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            limit=request.limit,
            offset=request.offset,
        )
        return ComplianceModulesetPublicationsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_compliance_moduleset_responsibles",
        description=(
            "Return groups responsible for one OpenSVC Collector compliance "
            "moduleset, selected by Collector moduleset id or exact moduleset "
            "name. Use this to know which groups can maintain or administer a moduleset."
        ),
        tags={"compliance", "modulesets", "groups", "responsibles", "read"},
        annotations={
            "title": "Get OpenSVC Compliance Moduleset Responsibles",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_compliance_moduleset_responsibles(
        request: Annotated[
            ComplianceModulesetResponsiblesRequest,
            Field(
                description=(
                    "Collector moduleset id or exact modset_name plus optional "
                    "filters, properties, ordering, search, limit, and offset. "
                    "Returns groups responsible for the moduleset."
                ),
            ),
        ],
    ) -> ComplianceModulesetResponsiblesResponse:
        """Return groups responsible for one compliance moduleset."""
        response = await core_get_compliance_moduleset_responsibles(
            moduleset_id=request.moduleset_id,
            modset_name=request.modset_name,
            filters=request.filters,
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            limit=request.limit,
            offset=request.offset,
        )
        return ComplianceModulesetResponsiblesResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_compliance_moduleset_candidate_services",
        description=(
            "Return services eligible or attachable to one OpenSVC Collector compliance "
            "moduleset according to Collector targeting rules. This does not mean "
            "the services are directly attached; use get_compliance_moduleset_services "
            "for direct attachments. Use this when users ask which services are "
            "targeted, eligible, candidate, concerned, or could receive a moduleset."
        ),
        tags={"compliance", "modulesets", "services", "candidate", "read"},
        annotations={
            "title": "Get OpenSVC Compliance Moduleset Candidate Services",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_compliance_moduleset_candidate_services(
        request: Annotated[
            ComplianceModulesetCandidateServicesRequest,
            Field(
                description=(
                    "Collector moduleset id or exact modset_name plus optional "
                    "filters, properties, ordering, search, limit, and offset. "
                    "Returns eligible/attachable candidate services, not direct attachments."
                ),
            ),
        ],
    ) -> ComplianceModulesetCandidateServicesResponse:
        """Return services eligible or attachable to one compliance moduleset."""
        response = await core_get_compliance_moduleset_candidate_services(
            moduleset_id=request.moduleset_id,
            modset_name=request.modset_name,
            filters=request.filters,
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            limit=request.limit,
            offset=request.offset,
        )
        return ComplianceModulesetCandidateServicesResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_compliance_moduleset_candidate_nodes",
        description=(
            "Return nodes eligible or attachable to one OpenSVC Collector compliance "
            "moduleset according to Collector targeting rules. This does not mean "
            "the nodes are directly attached; use get_compliance_moduleset_nodes "
            "for direct attachments. Use this when users ask which nodes are "
            "targeted, eligible, candidate, concerned, or could receive a moduleset."
        ),
        tags={"compliance", "modulesets", "nodes", "candidate", "read"},
        annotations={
            "title": "Get OpenSVC Compliance Moduleset Candidate Nodes",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_compliance_moduleset_candidate_nodes(
        request: Annotated[
            ComplianceModulesetCandidateNodesRequest,
            Field(
                description=(
                    "Collector moduleset id or exact modset_name plus optional "
                    "filters, properties, ordering, search, limit, and offset. "
                    "Returns eligible/attachable candidate nodes, not direct attachments."
                ),
            ),
        ],
    ) -> ComplianceModulesetCandidateNodesResponse:
        """Return nodes eligible or attachable to one compliance moduleset."""
        response = await core_get_compliance_moduleset_candidate_nodes(
            moduleset_id=request.moduleset_id,
            modset_name=request.modset_name,
            filters=request.filters,
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            limit=request.limit,
            offset=request.offset,
        )
        return ComplianceModulesetCandidateNodesResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_compliance_moduleset_usage",
        description=(
            "Return where one OpenSVC Collector compliance moduleset is reused "
            "or referenced, selected by Collector moduleset id or exact moduleset "
            "name. The returned sections depend on Collector /usage data."
        ),
        tags={"compliance", "modulesets", "usage", "read"},
        annotations={
            "title": "Get OpenSVC Compliance Moduleset Usage",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_compliance_moduleset_usage(
        request: Annotated[
            ComplianceModulesetUsageRequest,
            Field(
                description=(
                    "Collector moduleset id or exact modset_name used to retrieve "
                    "where the compliance moduleset is referenced."
                ),
            ),
        ],
    ) -> ComplianceModulesetUsageResponse:
        """Return where one compliance moduleset is referenced."""
        response = await core_get_compliance_moduleset_usage(
            moduleset_id=request.moduleset_id,
            modset_name=request.modset_name,
        )
        return ComplianceModulesetUsageResponse.model_validate(response)

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

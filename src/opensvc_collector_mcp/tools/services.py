from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from opensvc_collector_mcp.config import TOOL_TIMEOUT_SECONDS
from opensvc_collector_mcp.core.services_core import (
    count_services as core_count_services,
    get_service as core_get_service,
    get_service_actions as core_get_service_actions,
    get_service_unacknowledged_errors as core_get_service_unacknowledged_errors,
    get_service_health as core_get_service_health,
    get_service_instances as core_get_service_instances,
    get_service_resources as core_get_service_resources,
    list_service_props as core_list_service_props,
    list_services as core_list_services,
    search_frozen_services as core_search_frozen_services,
    search_services as core_search_services,
)
from opensvc_collector_mcp.models.services_model import (
    CountServicesRequest,
    CountServicesResponse,
    FrozenServicesRequest,
    FrozenServicesResponse,
    ListServicesRequest,
    SearchServicesRequest,
    ServiceActionsRequest,
    ServiceActionsResponse,
    ServiceUnacknowledgedErrorsRequest,
    ServiceUnacknowledgedErrorsResponse,
    ServiceHealthResponse,
    ServiceInstancesResponse,
    ServiceNameRequest,
    ServicePropsResponse,
    ServiceResourcesResponse,
    ServiceRowsResponse,
)


def register_services_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="list_services",
        description=(
            "List all OpenSVC Collector services using a compact inventory view "
            "by default. Use props to choose returned fields. Do not use this "
            "for filtered lookup; use search_services instead."
        ),
        tags={"services", "inventory", "read"},
        annotations={
            "title": "List OpenSVC Services",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def list_services(
        request: Annotated[
            ListServicesRequest,
            Field(description="Optional service listing parameters."),
        ] = ListServicesRequest(),
    ) -> ServiceRowsResponse:
        """Return OpenSVC Collector services and their selected properties."""
        response = await core_list_services(props=request.props)
        return ServiceRowsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="list_service_props",
        description=(
            "List available OpenSVC Collector service properties. "
            "Use service_props values as props or exact-match filter names for "
            "service tools."
        ),
        tags={"services", "inventory", "schema", "read"},
        annotations={
            "title": "List OpenSVC Service Properties",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def list_service_props() -> ServicePropsResponse:
        """Return the available service properties exposed by the Collector."""
        response = await core_list_service_props()
        return ServicePropsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="search_services",
        description=(
            "Search OpenSVC Collector services using exact-match filters only, "
            "with explicit limit and offset. Use list_service_props to discover "
            "valid filter and props fields."
        ),
        tags={"services", "inventory", "search", "read"},
        annotations={
            "title": "Search OpenSVC Services",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def search_services(
        request: Annotated[
            SearchServicesRequest,
            Field(
                description=(
                    "Search criteria, pagination, and returned properties for "
                    "service inventory lookup."
                ),
            ),
        ],
    ) -> ServiceRowsResponse:
        """Search services by exact-match service fields."""
        response = await core_search_services(
            filters=request.merged_filters(),
            props=request.props,
            limit=request.limit,
            offset=request.offset,
        )
        return ServiceRowsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="count_services",
        description=(
            "Count OpenSVC Collector services matching exact-match service filters. "
            "Use this when only the number of matching services is needed."
        ),
        tags={"services", "inventory", "count", "read"},
        annotations={
            "title": "Count OpenSVC Services",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def count_services(
        request: Annotated[
            CountServicesRequest,
            Field(description="Exact-match filters used to count Collector services."),
        ],
    ) -> CountServicesResponse:
        """Return the number of services matching the provided filters."""
        response = await core_count_services(filters=request.merged_filters())
        return CountServicesResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="search_frozen_services",
        description=(
            "Search OpenSVC services with currently frozen monitor instances. "
            "Accepts the same exact-match service filters as search_services, "
            "plus min_frozen_days to find services frozen longer than a threshold."
        ),
        tags={"services", "frozen", "inventory", "health", "read"},
        annotations={
            "title": "Search Frozen OpenSVC Services",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def search_frozen_services(
        request: Annotated[
            FrozenServicesRequest,
            Field(
                description=(
                    "Frozen service search criteria. Use filters or typed service "
                    "fields for exact service property matching, and min_frozen_days "
                    "for age filtering."
                ),
            ),
        ] = FrozenServicesRequest(),
    ) -> FrozenServicesResponse:
        """Return services with currently frozen monitor instances."""
        response = await core_search_frozen_services(
            filters=request.merged_filters(),
            min_frozen_days=request.min_frozen_days,
        )
        return FrozenServicesResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_service",
        description=(
            "Return full OpenSVC Collector details for one service selected by "
            "exact svcname. Use search_services first when the exact svcname is "
            "unknown."
        ),
        tags={"services", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Service",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_service(
        request: Annotated[
            ServiceNameRequest,
            Field(description="Service identifier used to retrieve full Collector details."),
        ],
    ) -> ServiceRowsResponse:
        """Return all available properties for one OpenSVC Collector service."""
        response = await core_get_service(svcname=request.svcname)
        return ServiceRowsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_service_instances",
        description=(
            "Return node-level OpenSVC Collector instances for one service selected "
            "by exact svcname. Use this to see where a service runs and its monitor "
            "state per node."
        ),
        tags={"services", "instances", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Service Instances",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_service_instances(
        request: Annotated[
            ServiceNameRequest,
            Field(
                description=(
                    "Exact service name used to list node-level instances through "
                    "Collector /services_instances."
                ),
            ),
        ],
    ) -> ServiceInstancesResponse:
        """Return node-level service instances for one OpenSVC Collector service."""
        response = await core_get_service_instances(svcname=request.svcname)
        return ServiceInstancesResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_service_resources",
        description=(
            "Return OpenSVC service resources for one service selected by exact "
            "svcname. The tool reads /services/<svcname>/resinfo and groups "
            "Collector key/value rows by resource id and node."
        ),
        tags={"services", "resources", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Service Resources",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_service_resources(
        request: Annotated[
            ServiceNameRequest,
            Field(
                description=(
                    "Exact service name used to list grouped resource information "
                    "through Collector /services/<svcname>/resinfo."
                ),
            ),
        ],
    ) -> ServiceResourcesResponse:
        """Return grouped resource information for one OpenSVC Collector service."""
        response = await core_get_service_resources(svcname=request.svcname)
        return ServiceResourcesResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_service_actions",
        description=(
            "Return recent or paginated OpenSVC action history for one service. "
            "Use status or action filters for targeted history, latest=true for "
            "the newest matching actions, and include_status_log only when full "
            "logs are explicitly needed."
        ),
        tags={"services", "actions", "history", "read"},
        annotations={
            "title": "Get OpenSVC Service Actions",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_service_actions(
        request: Annotated[
            ServiceActionsRequest,
            Field(
                description=(
                    "Exact service name, action filters, pagination, and status_log "
                    "options used to inspect service action history."
                ),
            ),
        ],
    ) -> ServiceActionsResponse:
        'Return service action history for one OpenSVC Collector service.'
        response = await core_get_service_actions(
            svcname=request.svcname,
            filters=request.merged_filters(),
            limit=request.limit,
            offset=request.offset,
            latest=request.latest,
            latest_first=request.latest_first,
            include_status_log=request.include_status_log,
            include_status_log_preview=request.include_status_log_preview,
            status_log_max_chars=request.status_log_max_chars,
        )
        return ServiceActionsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_service_unacknowledged_errors",
        description=(
            "Return recent or paginated unacknowledged OpenSVC action errors "
            "for one service. The Collector endpoint is already scoped to error "
            "actions that are not acknowledged, so use action, rid, or subset "
            "filters only to narrow the result."
        ),
        tags={"services", "actions", "errors", "history", "read"},
        annotations={
            "title": "Get OpenSVC Service Unacknowledged Errors",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_service_unacknowledged_errors(
        request: Annotated[
            ServiceUnacknowledgedErrorsRequest,
            Field(
                description=(
                    "Exact service name, optional action filters, pagination, "
                    "and status_log options used to inspect unacknowledged "
                    "service action errors."
                ),
            ),
        ],
    ) -> ServiceUnacknowledgedErrorsResponse:
        'Return unacknowledged service action errors for one service.'
        response = await core_get_service_unacknowledged_errors(
            svcname=request.svcname,
            filters=request.merged_filters(),
            limit=request.limit,
            offset=request.offset,
            latest=request.latest,
            latest_first=request.latest_first,
            include_status_log=request.include_status_log,
            include_status_log_preview=request.include_status_log_preview,
            status_log_max_chars=request.status_log_max_chars,
        )
        return ServiceUnacknowledgedErrorsResponse.model_validate(response)


    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_service_health",
        description=(
            "Return an interpreted health summary for one OpenSVC service selected "
            "by exact svcname. The tool combines service status, availability, "
            "frozen state, placement, and per-node monitor state."
        ),
        tags={"services", "health", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Service Health",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_service_health(
        request: Annotated[
            ServiceNameRequest,
            Field(
                description=(
                    "Exact service name used to compute a health summary from "
                    "Collector service and service instance state."
                ),
            ),
        ],
    ) -> ServiceHealthResponse:
        """Return interpreted health signals and issues for one service."""
        response = await core_get_service_health(svcname=request.svcname)
        return ServiceHealthResponse.model_validate(response)

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from opensvc_collector_mcp.config import TOOL_TIMEOUT_SECONDS
from opensvc_collector_mcp.core.services import (
    count_services as core_count_services,
    get_service as core_get_service,
    get_service_actions as core_get_service_actions,
    get_service_alerts as core_get_service_alerts,
    get_service_checks as core_get_service_checks,
    get_service_compliance_status as core_get_service_compliance_status,
    get_service_config as core_get_service_config,
    get_service_disks as core_get_service_disks,
    get_service_hbas as core_get_service_hbas,
    get_service_targets as core_get_service_targets,
    get_service_status_history as core_get_service_status_history,
    get_service_unacknowledged_errors as core_get_service_unacknowledged_errors,
    get_service_health as core_get_service_health,
    get_service_instances as core_get_service_instances,
    get_service_nodes as core_get_service_nodes,
    get_service_resources as core_get_service_resources,
    get_service_resource_status as core_get_service_resource_status,
    get_service_tags as core_get_service_tags,
    list_service_props as core_list_service_props,
    list_services as core_list_services,
    search_frozen_services as core_search_frozen_services,
    search_services as core_search_services,
    search_services_by_tag as core_search_services_by_tag,
    search_services_without_tag as core_search_services_without_tag,
)
from opensvc_collector_mcp.models.services import (
    CountServicesRequest,
    CountServicesResponse,
    FrozenServicesRequest,
    FrozenServicesResponse,
    ListServicesRequest,
    SearchServicesRequest,
    ServiceActionsRequest,
    ServiceActionsResponse,
    ServiceAlertsRequest,
    ServiceAlertsResponse,
    ServiceChecksRequest,
    ServiceChecksResponse,
    ServiceComplianceStatusRequest,
    ServiceComplianceStatusResponse,
    ServiceConfigRequest,
    ServiceConfigResponse,
    ServiceDisksRequest,
    ServiceDisksResponse,
    ServiceUnacknowledgedErrorsRequest,
    ServiceUnacknowledgedErrorsResponse,
    ServiceHbasRequest,
    ServiceHbasResponse,
    ServiceHealthResponse,
    ServiceInstancesResponse,
    ServiceNameRequest,
    ServiceNodesRequest,
    ServiceNodesResponse,
    ServicePropsResponse,
    ServiceResourcesResponse,
    ServiceResourceStatusRequest,
    ServiceResourceStatusResponse,
    ServiceTagsRequest,
    ServiceTagsResponse,
    ServiceTargetsRequest,
    ServiceTargetsResponse,
    ServiceStatusHistoryRequest,
    ServiceStatusHistoryResponse,
    ServiceTagSearchRequest,
    ServicesByTagResponse,
    ServicesWithoutTagResponse,
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
        name="get_service_config",
        description=(
            "Return the OpenSVC configuration for one service selected by exact "
            "svcname. The tool reads /services/<svcname> with props limited to "
            "svc_config metadata, and returns raw config text plus parsed sections."
        ),
        tags={"services", "config", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Service Config",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_service_config(
        request: Annotated[
            ServiceConfigRequest,
            Field(
                description=(
                    "Exact service name and output options used to retrieve the "
                    "service configuration from Collector svc_config."
                ),
            ),
        ],
    ) -> ServiceConfigResponse:
        'Return raw and parsed OpenSVC configuration for one service.'
        response = await core_get_service_config(
            svcname=request.svcname,
            include_raw_config=request.include_raw_config,
            include_sections=request.include_sections,
            raw_config_max_chars=request.raw_config_max_chars,
        )
        return ServiceConfigResponse.model_validate(response)


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
        name="get_service_nodes",
        description=(
            "Return Collector node monitor rows for one service selected by exact "
            "svcname. Use this to see which nodes know the service and the "
            "per-node overall, availability, frozen, and update statuses."
        ),
        tags={"services", "nodes", "instances", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Service Nodes",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_service_nodes(
        request: Annotated[
            ServiceNodesRequest,
            Field(
                description=(
                    "Exact service name, optional returned properties, and "
                    "internal pagination guardrails used to list Collector "
                    "node monitor rows through /services/<svcname>/nodes."
                ),
            ),
        ],
    ) -> ServiceNodesResponse:
        'Return node monitor rows for one OpenSVC Collector service.'
        response = await core_get_service_nodes(
            svcname=request.svcname,
            props=request.props,
            page_size=request.page_size,
            max_nodes=request.max_nodes,
        )
        return ServiceNodesResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_service_hbas",
        description=(
            "Return HBA rows attached to one OpenSVC service selected by exact "
            "svcname. The tool reads /services/<svcname>/hbas and returns a "
            "flat view with node, HBA id, HBA type, and update time."
        ),
        tags={"services", "hbas", "storage", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Service HBAs",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_service_hbas(
        request: Annotated[
            ServiceHbasRequest,
            Field(
                description=(
                    "Exact service name, optional returned properties, and "
                    "internal pagination guardrails used to list HBAs through "
                    "Collector /services/<svcname>/hbas."
                ),
            ),
        ],
    ) -> ServiceHbasResponse:
        'Return HBA rows attached to one OpenSVC Collector service.'
        response = await core_get_service_hbas(
            svcname=request.svcname,
            props=request.props,
            page_size=request.page_size,
            max_hbas=request.max_hbas,
        )
        return ServiceHbasResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_service_targets",
        description=(
            "Return storage target rows attached to one OpenSVC service selected "
            "by exact svcname. The tool reads /services/<svcname>/targets and "
            "can filter by hba_id, node_id, tgt_id, or array_name."
        ),
        tags={"services", "targets", "storage", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Service Storage Targets",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_service_targets(
        request: Annotated[
            ServiceTargetsRequest,
            Field(
                description=(
                    "Exact service name, optional exact-match target filters, "
                    "returned properties, and internal pagination guardrails "
                    "used to list targets through /services/<svcname>/targets."
                ),
            ),
        ],
    ) -> ServiceTargetsResponse:
        'Return storage target rows attached to one OpenSVC Collector service.'
        response = await core_get_service_targets(
            svcname=request.svcname,
            filters=request.merged_filters(),
            props=request.props,
            page_size=request.page_size,
            max_targets=request.max_targets,
        )
        return ServiceTargetsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_service_disks",
        description=(
            "Return disk rows attached to one OpenSVC service selected by exact "
            "svcname. The tool reads /services/<svcname>/disks and returns a "
            "flat disk view with node, size, local/SAN, diskinfo, and storage "
            "array fields."
        ),
        tags={"services", "disks", "storage", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Service Disks",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_service_disks(
        request: Annotated[
            ServiceDisksRequest,
            Field(
                description=(
                    "Exact service name, optional returned properties, and "
                    "internal pagination guardrails used to list disks through "
                    "Collector /services/<svcname>/disks."
                ),
            ),
        ],
    ) -> ServiceDisksResponse:
        'Return disk rows attached to one OpenSVC Collector service.'
        response = await core_get_service_disks(
            svcname=request.svcname,
            props=request.props,
            page_size=request.page_size,
            max_disks=request.max_disks,
        )
        return ServiceDisksResponse.model_validate(response)

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
        name="get_service_compliance_status",
        description=(
            "Return current OpenSVC compliance status rows for one service selected "
            "by exact svcname. The tool reads /services/<svcname>/compliance/status, "
            "summarizes OK and non-OK module counts, and includes a bounded "
            "run_log_preview by default for diagnostics."
        ),
        tags={"services", "compliance", "status", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Service Compliance Status",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_service_compliance_status(
        request: Annotated[
            ServiceComplianceStatusRequest,
            Field(
                description=(
                    "Exact service name, optional exact-match compliance filters, "
                    "returned properties, pagination guardrails, and run_log "
                    "output options used to inspect current service compliance "
                    "status through Collector /services/<svcname>/compliance/status."
                ),
            ),
        ],
    ) -> ServiceComplianceStatusResponse:
        'Return current compliance status rows for one OpenSVC Collector service.'
        response = await core_get_service_compliance_status(
            svcname=request.svcname,
            filters=request.merged_filters(),
            props=request.props,
            page_size=request.page_size,
            max_status=request.max_status,
            include_run_log=request.include_run_log,
            include_run_log_preview=request.include_run_log_preview,
            run_log_max_chars=request.run_log_max_chars,
        )
        return ServiceComplianceStatusResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_service_resource_status",
        description=(
            "Return runtime OpenSVC resource status rows for one service selected "
            "by exact svcname. The tool reads /services/<svcname>/resources and "
            "returns flat per-node resource state such as rid, type, status, "
            "monitor flags, description, and timestamps."
        ),
        tags={"services", "resources", "status", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Service Resource Status",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_service_resource_status(
        request: Annotated[
            ServiceResourceStatusRequest,
            Field(
                description=(
                    "Exact service name, optional exact-match runtime resource "
                    "filters, returned properties, and internal pagination "
                    "guardrails used to list resource status through Collector "
                    "/services/<svcname>/resources."
                ),
            ),
        ],
    ) -> ServiceResourceStatusResponse:
        'Return runtime resource status rows for one OpenSVC Collector service.'
        response = await core_get_service_resource_status(
            svcname=request.svcname,
            filters=request.merged_filters(),
            props=request.props,
            page_size=request.page_size,
            max_resources=request.max_resources,
        )
        return ServiceResourceStatusResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="search_services_by_tag",
        description=(
            "Return OpenSVC services that have one exact Collector tag attached. "
            "The tool resolves tag_name through /tags, then lists services via "
            "/tags/<tag_id>/services using internal paged reads."
        ),
        tags={"services", "tags", "search", "read"},
        annotations={
            "title": "Search OpenSVC Services By Tag",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def search_services_by_tag(
        request: Annotated[
            ServiceTagSearchRequest,
            Field(
                description=(
                    "Exact tag name, returned service properties, and internal "
                    "pagination guardrails."
                ),
            ),
        ],
    ) -> ServicesByTagResponse:
        'Return services attached to one exact OpenSVC Collector tag.'
        response = await core_search_services_by_tag(
            tag_name=request.tag_name,
            props=request.props,
            page_size=request.page_size,
            max_services=request.max_services,
        )
        return ServicesByTagResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="search_services_without_tag",
        description=(
            "Return OpenSVC services that do not have one exact Collector tag "
            "attached. The tool resolves tag_name, lists tagged services, lists "
            "all services, then returns the difference."
        ),
        tags={"services", "tags", "search", "read"},
        annotations={
            "title": "Search OpenSVC Services Without Tag",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def search_services_without_tag(
        request: Annotated[
            ServiceTagSearchRequest,
            Field(
                description=(
                    "Exact tag name to exclude, returned service properties, "
                    "and internal pagination guardrails."
                ),
            ),
        ],
    ) -> ServicesWithoutTagResponse:
        'Return services that do not have one exact OpenSVC Collector tag.'
        response = await core_search_services_without_tag(
            tag_name=request.tag_name,
            props=request.props,
            page_size=request.page_size,
            max_services=request.max_services,
        )
        return ServicesWithoutTagResponse.model_validate(response)


    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_service_tags",
        description=(
            "Return OpenSVC Collector tags attached to one service selected by "
            "exact svcname. The tool retrieves all matching tags using internal "
            "paged Collector reads and compact tag properties by default."
        ),
        tags={"services", "tags", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Service Tags",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_service_tags(
        request: Annotated[
            ServiceTagsRequest,
            Field(
                description=(
                    "Exact service name, optional exact-match tag filters, "
                    "returned properties, and internal pagination guardrails."
                ),
            ),
        ],
    ) -> ServiceTagsResponse:
        'Return tags attached to one OpenSVC Collector service.'
        response = await core_get_service_tags(
            svcname=request.svcname,
            filters=request.merged_filters(),
            props=request.props,
            page_size=request.page_size,
            max_tags=request.max_tags,
        )
        return ServiceTagsResponse.model_validate(response)


    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_service_checks",
        description=(
            "Return live OpenSVC Collector checks for one service selected by exact "
            "svcname. The tool retrieves all matching checks using internal paged "
            "Collector reads and compact check properties by default."
        ),
        tags={"services", "checks", "health", "read"},
        annotations={
            "title": "Get OpenSVC Service Checks",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_service_checks(
        request: Annotated[
            ServiceChecksRequest,
            Field(
                description=(
                    "Exact service name, optional exact-match check filters, "
                    "returned properties, and internal pagination guardrails."
                ),
            ),
        ],
    ) -> ServiceChecksResponse:
        'Return live Collector checks for one OpenSVC service.'
        response = await core_get_service_checks(
            svcname=request.svcname,
            filters=request.merged_filters(),
            props=request.props,
            page_size=request.page_size,
            max_checks=request.max_checks,
        )
        return ServiceChecksResponse.model_validate(response)


    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_service_alerts",
        description=(
            "Return current OpenSVC Collector dashboard alerts for one service "
            "selected by exact svcname. Use this for active service alerts, not "
            "historical action logs or interpreted health summaries."
        ),
        tags={"services", "alerts", "health", "read"},
        annotations={
            "title": "Get OpenSVC Service Alerts",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_service_alerts(
        request: Annotated[
            ServiceAlertsRequest,
            Field(
                description=(
                    "Exact service name, optional exact-match alert filters, "
                    "pagination, and returned properties."
                ),
            ),
        ],
    ) -> ServiceAlertsResponse:
        'Return current dashboard alerts for one OpenSVC Collector service.'
        response = await core_get_service_alerts(
            svcname=request.svcname,
            filters=request.merged_filters(),
            props=request.props,
            limit=request.limit,
            offset=request.offset,
        )
        return ServiceAlertsResponse.model_validate(response)


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
        name="get_service_status_history",
        description=(
            "Return availability status history for one OpenSVC service selected "
            "by exact svcname. The tool resolves svc_id, reads /services_status_log, "
            "and returns sorted status periods plus the best current_status_since."
        ),
        tags={"services", "status", "history", "health", "read"},
        annotations={
            "title": "Get OpenSVC Service Status History",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_service_status_history(
        request: Annotated[
            ServiceStatusHistoryRequest,
            Field(
                description=(
                    "Exact service name, optional availability status filters, "
                    "pagination, and internal scan guardrails used to inspect "
                    "service availability status history."
                ),
            ),
        ],
    ) -> ServiceStatusHistoryResponse:
        'Return availability status history for one OpenSVC Collector service.'
        response = await core_get_service_status_history(
            svcname=request.svcname,
            filters=request.merged_filters(),
            props=request.props,
            limit=request.limit,
            offset=request.offset,
            latest=request.latest,
            latest_first=request.latest_first,
            page_size=request.page_size,
            max_history=request.max_history,
        )
        return ServiceStatusHistoryResponse.model_validate(response)

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

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from opensvc_collector_mcp.config import TOOL_TIMEOUT_SECONDS
from opensvc_collector_mcp.core.services_core import (
    count_services as core_count_services,
    list_service_props as core_list_service_props,
    list_services as core_list_services,
    search_services as core_search_services,
)
from opensvc_collector_mcp.models.services_model import (
    CountServicesRequest,
    CountServicesResponse,
    ListServicesRequest,
    SearchServicesRequest,
    ServicePropsResponse,
    ServiceRowsResponse,
)


def register_services_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="list_services",
        description=(
            "List OpenSVC Collector services using a compact service inventory "
            "view by default. Use props to choose explicit service fields."
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
            "Use this before service list or search tools to choose valid props."
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
            "Search OpenSVC Collector services using exact-match service filters. "
            "Use list_service_props to discover valid filter and props fields."
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

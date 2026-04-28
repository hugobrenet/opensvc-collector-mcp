from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from opensvc_collector_mcp.config import TOOL_TIMEOUT_SECONDS
from opensvc_collector_mcp.core.services_core import (
    list_service_props as core_list_service_props,
    list_services as core_list_services,
)
from opensvc_collector_mcp.models.services_model import (
    ListServicesRequest,
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

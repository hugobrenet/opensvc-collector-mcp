from fastmcp import FastMCP

from opensvc_collector_mcp.config import TOOL_TIMEOUT_SECONDS
from opensvc_collector_mcp.core.services_core import (
    list_service_props as core_list_service_props,
)
from opensvc_collector_mcp.models.services_model import ServicePropsResponse


def register_services_tools(mcp: FastMCP) -> None:
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

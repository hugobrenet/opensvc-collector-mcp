from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from opensvc_collector_mcp.config import TOOL_TIMEOUT_SECONDS
from opensvc_collector_mcp.core.apps import (
    list_app_props as core_list_app_props,
    list_apps as core_list_apps,
)
from opensvc_collector_mcp.models.apps import (
    AppPropsResponse,
    AppRowsResponse,
    ListAppsRequest,
)


def register_apps_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="list_apps",
        description=(
            "List or search OpenSVC Collector application codes using "
            "exact-match filters, Collector search, pagination, ordering, "
            "and selectable props. Defaults to a compact app inventory view."
        ),
        tags={"apps", "inventory", "read"},
        annotations={
            "title": "List OpenSVC Apps",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def list_apps(
        request: Annotated[
            ListAppsRequest,
            Field(description="Optional app listing parameters."),
        ] = ListAppsRequest(),
    ) -> AppRowsResponse:
        """Return OpenSVC Collector apps and their selected properties."""
        response = await core_list_apps(
            filters=request.merged_filters(),
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            limit=request.limit,
            offset=request.offset,
        )
        return AppRowsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="list_app_props",
        description=(
            "List available OpenSVC Collector app properties. "
            "Use this before list_apps to choose valid props and "
            "exact-match filter names."
        ),
        tags={"apps", "inventory", "schema", "read"},
        annotations={
            "title": "List OpenSVC App Properties",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def list_app_props() -> AppPropsResponse:
        """Return the available app properties exposed by the Collector."""
        response = await core_list_app_props()
        return AppPropsResponse.model_validate(response)

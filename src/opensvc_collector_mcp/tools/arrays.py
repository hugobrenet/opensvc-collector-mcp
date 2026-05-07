from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from opensvc_collector_mcp.config import TOOL_TIMEOUT_SECONDS
from opensvc_collector_mcp.core.arrays import (
    list_array_props as core_list_array_props,
    list_arrays as core_list_arrays,
)
from opensvc_collector_mcp.models.arrays import (
    ArrayPropsResponse,
    ArrayRowsResponse,
    ListArraysRequest,
)


def register_arrays_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="list_arrays",
        description=(
            "List or search OpenSVC Collector storage arrays using exact-match "
            "filters, Collector search, pagination, ordering, and selectable "
            "props. Defaults to a compact array inventory view."
        ),
        tags={"arrays", "storage", "inventory", "read"},
        annotations={
            "title": "List OpenSVC Storage Arrays",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def list_arrays(
        request: Annotated[
            ListArraysRequest,
            Field(description="Optional array listing parameters."),
        ] = ListArraysRequest(),
    ) -> ArrayRowsResponse:
        """Return OpenSVC Collector storage arrays and selected properties."""
        response = await core_list_arrays(
            filters=request.merged_filters(),
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            limit=request.limit,
            offset=request.offset,
        )
        return ArrayRowsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="list_array_props",
        description=(
            "List available OpenSVC Collector storage array properties. "
            "Use this before list_arrays to choose valid props and "
            "exact-match filter names."
        ),
        tags={"arrays", "storage", "inventory", "schema", "read"},
        annotations={
            "title": "List OpenSVC Storage Array Properties",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def list_array_props() -> ArrayPropsResponse:
        """Return the available storage array properties exposed by Collector."""
        response = await core_list_array_props()
        return ArrayPropsResponse.model_validate(response)

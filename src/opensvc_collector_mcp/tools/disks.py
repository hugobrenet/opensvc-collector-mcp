from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from opensvc_collector_mcp.config import TOOL_TIMEOUT_SECONDS
from opensvc_collector_mcp.core.disks import (
    count_disks as core_count_disks,
    get_disk as core_get_disk,
    list_disk_props as core_list_disk_props,
    list_disks as core_list_disks,
)
from opensvc_collector_mcp.models.disks import (
    CountDisksRequest,
    CountDisksResponse,
    DiskDetailResponse,
    DiskPropsResponse,
    DiskRowsResponse,
    GetDiskRequest,
    ListDisksRequest,
)


def register_disks_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="list_disks",
        description=(
            "List or search OpenSVC Collector disks using exact-match filters, "
            "Collector search, pagination, ordering, and selectable props. "
            "Defaults to a compact flat disk inventory view."
        ),
        tags={"disks", "storage", "inventory", "read"},
        annotations={
            "title": "List OpenSVC Disks",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def list_disks(
        request: Annotated[
            ListDisksRequest,
            Field(description="Optional disk listing parameters."),
        ] = ListDisksRequest(),
    ) -> DiskRowsResponse:
        """Return OpenSVC Collector disks and selected properties."""
        response = await core_list_disks(
            filters=request.merged_filters(),
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            limit=request.limit,
            offset=request.offset,
        )
        return DiskRowsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="count_disks",
        description=(
            "Count OpenSVC Collector disk rows matching exact-match filters. "
            "Use this when only the number of matching disks is needed."
        ),
        tags={"disks", "storage", "inventory", "count", "read"},
        annotations={
            "title": "Count OpenSVC Disks",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def count_disks(
        request: Annotated[
            CountDisksRequest,
            Field(description="Exact-match filters used to count Collector disks."),
        ] = CountDisksRequest(),
    ) -> CountDisksResponse:
        """Return the number of disks matching the provided filters."""
        response = await core_count_disks(
            filters=request.merged_filters(),
            search=request.search,
        )
        return CountDisksResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_disk",
        description=(
            "Return OpenSVC Collector details for one disk selected by stable "
            "Collector disk_id. The /disks/<id> endpoint expects disk_id, not "
            "svcdisks.id or diskinfo.id row ids."
        ),
        tags={"disks", "storage", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Disk",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_disk(
        request: Annotated[
            GetDiskRequest,
            Field(description="Disk selector and optional property selection."),
        ],
    ) -> DiskDetailResponse:
        """Return one OpenSVC Collector disk by stable disk_id."""
        response = await core_get_disk(disk=request.disk, props=request.props)
        return DiskDetailResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="list_disk_props",
        description=(
            "Return disk properties exposed by OpenSVC Collector /disks. "
            "Use this before selecting props or building generic filters."
        ),
        tags={"disks", "storage", "props", "inventory", "read"},
        annotations={
            "title": "List OpenSVC Disk Properties",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def list_disk_props() -> DiskPropsResponse:
        """Return disk properties exposed by Collector."""
        response = await core_list_disk_props()
        return DiskPropsResponse.model_validate(response)

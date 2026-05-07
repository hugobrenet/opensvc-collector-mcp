from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from opensvc_collector_mcp.config import TOOL_TIMEOUT_SECONDS
from opensvc_collector_mcp.core.arrays import (
    count_array_diskgroups as core_count_array_diskgroups,
    count_arrays as core_count_arrays,
    get_array as core_get_array,
    get_array_diskgroup as core_get_array_diskgroup,
    get_array_diskgroup_quota as core_get_array_diskgroup_quota,
    get_array_diskgroup_quotas as core_get_array_diskgroup_quotas,
    get_array_diskgroups as core_get_array_diskgroups,
    get_array_proxies as core_get_array_proxies,
    get_array_targets as core_get_array_targets,
    list_array_diskgroups as core_list_array_diskgroups,
    list_array_props as core_list_array_props,
    list_arrays as core_list_arrays,
)
from opensvc_collector_mcp.models.arrays import (
    ArrayDiskgroupQuotaRequest,
    ArrayDiskgroupQuotaResponse,
    ArrayDiskgroupQuotasRequest,
    ArrayDiskgroupQuotasResponse,
    ArrayDiskgroupRequest,
    ArrayDiskgroupResponse,
    ArrayDiskgroupRowsResponse,
    ArrayDiskgroupsRequest,
    ArrayDiskgroupsResponse,
    ArrayPropsResponse,
    ArrayProxiesRequest,
    ArrayProxiesResponse,
    ArrayRelationCountRequest,
    ArrayRelationCountResponse,
    ArrayRowsResponse,
    ArrayTargetsRequest,
    ArrayTargetsResponse,
    CountArraysRequest,
    CountArraysResponse,
    GetArrayRequest,
    ListArrayDiskgroupsRequest,
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
        name="list_array_diskgroups",
        description=(
            "List or search OpenSVC Collector storage array diskgroups across "
            "all arrays using exact-match filters, Collector search, "
            "pagination, ordering, and selectable props."
        ),
        tags={"arrays", "storage", "diskgroups", "inventory", "read"},
        annotations={
            "title": "List OpenSVC Storage Array Diskgroups",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def list_array_diskgroups(
        request: Annotated[
            ListArrayDiskgroupsRequest,
            Field(description="Optional global diskgroup listing parameters."),
        ] = ListArrayDiskgroupsRequest(),
    ) -> ArrayDiskgroupRowsResponse:
        """Return OpenSVC Collector storage array diskgroups across arrays."""
        response = await core_list_array_diskgroups(
            filters=request.merged_filters(),
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            limit=request.limit,
            offset=request.offset,
        )
        return ArrayDiskgroupRowsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="count_arrays",
        description=(
            "Count OpenSVC Collector storage arrays matching exact-match "
            "filters. Use this when only the number of matching arrays "
            "is needed."
        ),
        tags={"arrays", "storage", "inventory", "count", "read"},
        annotations={
            "title": "Count OpenSVC Storage Arrays",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def count_arrays(
        request: Annotated[
            CountArraysRequest,
            Field(description="Exact-match filters used to count Collector arrays."),
        ] = CountArraysRequest(),
    ) -> CountArraysResponse:
        """Return the number of arrays matching the provided filters."""
        response = await core_count_arrays(
            filters=request.merged_filters(),
            search=request.search,
        )
        return CountArraysResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_array",
        description=(
            "Return OpenSVC Collector details for one storage array "
            "selected by exact array name or Collector array row id."
        ),
        tags={"arrays", "storage", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Storage Array",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_array(
        request: Annotated[
            GetArrayRequest,
            Field(description="Array selector and optional property selection."),
        ],
    ) -> ArrayRowsResponse:
        """Return one OpenSVC Collector storage array by name or row id."""
        response = await core_get_array(array=request.array, props=request.props)
        return ArrayRowsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="count_array_diskgroups",
        description=(
            "Count OpenSVC Collector diskgroups attached to one storage "
            "array selected by exact array name or Collector array row id. "
            "This uses a lightweight Collector count read from "
            "/arrays/<id>/diskgroups."
        ),
        tags={"arrays", "storage", "diskgroups", "count", "read"},
        annotations={
            "title": "Count OpenSVC Storage Array Diskgroups",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def count_array_diskgroups(
        request: Annotated[
            ArrayRelationCountRequest,
            Field(description="Array selector used to count attached diskgroups."),
        ],
    ) -> ArrayRelationCountResponse:
        """Return the number of diskgroups attached to one storage array."""
        response = await core_count_array_diskgroups(array=request.array)
        return ArrayRelationCountResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_array_diskgroup",
        description=(
            "Return OpenSVC Collector details for one storage array diskgroup "
            "selected by array name or id and diskgroup name or id."
        ),
        tags={"arrays", "storage", "diskgroups", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Storage Array Diskgroup",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_array_diskgroup(
        request: Annotated[
            ArrayDiskgroupRequest,
            Field(description="Array and diskgroup selectors with optional props."),
        ],
    ) -> ArrayDiskgroupResponse:
        """Return one diskgroup attached to one OpenSVC Collector storage array."""
        response = await core_get_array_diskgroup(
            array=request.array,
            diskgroup=request.diskgroup,
            props=request.props,
        )
        return ArrayDiskgroupResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_array_diskgroups",
        description=(
            "Return all OpenSVC Collector diskgroups attached to one storage "
            "array selected by exact array name or Collector array row id. "
            "The tool follows Collector pagination until complete or "
            "max_diskgroups is reached."
        ),
        tags={"arrays", "storage", "diskgroups", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Storage Array Diskgroups",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_array_diskgroups(
        request: Annotated[
            ArrayDiskgroupsRequest,
            Field(description="Array selector and optional diskgroup property selection."),
        ],
    ) -> ArrayDiskgroupsResponse:
        """Return diskgroups attached to one OpenSVC Collector storage array."""
        response = await core_get_array_diskgroups(
            array=request.array,
            props=request.props,
            max_diskgroups=request.max_diskgroups,
        )
        return ArrayDiskgroupsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_array_diskgroup_quotas",
        description=(
            "Return all OpenSVC Collector quota rows attached to one storage "
            "array diskgroup. The tool follows Collector pagination until "
            "complete or max_quotas is reached."
        ),
        tags={"arrays", "storage", "diskgroups", "quotas", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Storage Array Diskgroup Quotas",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_array_diskgroup_quotas(
        request: Annotated[
            ArrayDiskgroupQuotasRequest,
            Field(description="Array and diskgroup selectors with optional quota props."),
        ],
    ) -> ArrayDiskgroupQuotasResponse:
        """Return quota rows attached to one storage array diskgroup."""
        response = await core_get_array_diskgroup_quotas(
            array=request.array,
            diskgroup=request.diskgroup,
            props=request.props,
            max_quotas=request.max_quotas,
        )
        return ArrayDiskgroupQuotasResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_array_diskgroup_quota",
        description=(
            "Return OpenSVC Collector details for one quota row attached to "
            "one storage array diskgroup."
        ),
        tags={"arrays", "storage", "diskgroups", "quotas", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Storage Array Diskgroup Quota",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_array_diskgroup_quota(
        request: Annotated[
            ArrayDiskgroupQuotaRequest,
            Field(description="Array, diskgroup, and quota selectors with optional props."),
        ],
    ) -> ArrayDiskgroupQuotaResponse:
        """Return one quota row attached to one storage array diskgroup."""
        response = await core_get_array_diskgroup_quota(
            array=request.array,
            diskgroup=request.diskgroup,
            quota=request.quota,
            props=request.props,
        )
        return ArrayDiskgroupQuotaResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_array_proxies",
        description=(
            "Return all OpenSVC Collector proxy nodes attached to one storage "
            "array selected by exact array name or Collector array row id. "
            "The tool follows Collector pagination until complete or "
            "max_proxies is reached."
        ),
        tags={"arrays", "storage", "proxies", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Storage Array Proxies",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_array_proxies(
        request: Annotated[
            ArrayProxiesRequest,
            Field(description="Array selector and optional proxy property selection."),
        ],
    ) -> ArrayProxiesResponse:
        """Return proxy rows attached to one OpenSVC Collector storage array."""
        response = await core_get_array_proxies(
            array=request.array,
            props=request.props,
            max_proxies=request.max_proxies,
        )
        return ArrayProxiesResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_array_targets",
        description=(
            "Return all OpenSVC Collector target ids attached to one storage "
            "array selected by exact array name or Collector array row id. "
            "The tool follows Collector pagination until complete or "
            "max_targets is reached."
        ),
        tags={"arrays", "storage", "targets", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Storage Array Targets",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_array_targets(
        request: Annotated[
            ArrayTargetsRequest,
            Field(description="Array selector and optional target property selection."),
        ],
    ) -> ArrayTargetsResponse:
        """Return target id rows attached to one OpenSVC Collector storage array."""
        response = await core_get_array_targets(
            array=request.array,
            props=request.props,
            max_targets=request.max_targets,
        )
        return ArrayTargetsResponse.model_validate(response)

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

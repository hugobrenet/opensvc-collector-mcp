from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from opensvc_collector_mcp.config import TOOL_TIMEOUT_SECONDS
from opensvc_collector_mcp.core.tags import (
    count_tag_nodes as core_count_tag_nodes,
    count_tag_services as core_count_tag_services,
    count_tags as core_count_tags,
    create_tag as core_create_tag,
    get_tag as core_get_tag,
    get_tag_nodes as core_get_tag_nodes,
    get_tag_services as core_get_tag_services,
    list_tag_props as core_list_tag_props,
    list_tags as core_list_tags,
)
from opensvc_collector_mcp.models.tags import (
    CountTagServicesRequest,
    CountTagsRequest,
    CountTagsResponse,
    CreateTagRequest,
    CreateTagResponse,
    ListTagsRequest,
    TagIdentityRequest,
    TagNodesRequest,
    TagNodesResponse,
    TagPropsResponse,
    TagServicesRequest,
    TagServicesResponse,
    TagRelationCountResponse,
    TagRowsResponse,
    TagSelectorRequest,
)


def register_tags_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="create_tag",
        description=(
            "Create one OpenSVC Collector tag. Requires Collector TagManager "
            "or Manager privileges through MCP RBAC."
        ),
        tags={"tags", "write:tags"},
        annotations={
            "title": "Create OpenSVC Tag",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": False,
            "openWorldHint": False,
        },
    )
    async def create_tag(
        request: Annotated[
            CreateTagRequest,
            Field(description="Tag creation parameters."),
        ],
    ) -> CreateTagResponse:
        """Create an OpenSVC Collector tag."""
        response = await core_create_tag(
            tag_name=request.tag_name,
            tag_data=request.tag_data,
            tag_exclude=request.tag_exclude,
        )
        return CreateTagResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="list_tags",
        description=(
            "List or search OpenSVC Collector tags using exact-match filters, "
            "Collector search, pagination, ordering, and selectable props. "
            "Defaults to a compact tag inventory view."
        ),
        tags={"tags", "inventory", "read"},
        annotations={
            "title": "List OpenSVC Tags",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def list_tags(
        request: Annotated[
            ListTagsRequest,
            Field(description="Optional tag listing parameters."),
        ] = ListTagsRequest(),
    ) -> TagRowsResponse:
        """Return OpenSVC Collector tags and their selected properties."""
        response = await core_list_tags(
            filters=request.merged_filters(),
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            limit=request.limit,
            offset=request.offset,
        )
        return TagRowsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="count_tags",
        description=(
            "Count OpenSVC Collector tags matching exact-match tag filters. "
            "Use this when only the number of matching tags is needed."
        ),
        tags={"tags", "inventory", "count", "read"},
        annotations={
            "title": "Count OpenSVC Tags",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def count_tags(
        request: Annotated[
            CountTagsRequest,
            Field(description="Exact-match filters used to count Collector tags."),
        ] = CountTagsRequest(),
    ) -> CountTagsResponse:
        """Return the number of tags matching the provided filters."""
        response = await core_count_tags(filters=request.merged_filters())
        return CountTagsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_tag",
        description=(
            "Return OpenSVC Collector details for one tag selected by exact "
            "tag id or exact tag name. Use list_tags first when the exact "
            "identifier is unknown."
        ),
        tags={"tags", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Tag",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_tag(
        request: Annotated[
            TagSelectorRequest,
            Field(description="Tag selector and optional property selection."),
        ],
    ) -> TagRowsResponse:
        """Return one OpenSVC Collector tag by tag id or tag name."""
        response = await core_get_tag(
            tag_id=request.tag_id,
            tag_name=request.tag_name,
            props=request.props,
        )
        return TagRowsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_tag_nodes",
        description=(
            "Return all OpenSVC Collector nodes attached to one tag selected "
            "by exact tag id or exact tag name. The tool follows Collector "
            "pagination until complete or max_nodes is reached."
        ),
        tags={"tags", "nodes", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Tag Nodes",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_tag_nodes(
        request: Annotated[
            TagNodesRequest,
            Field(description="Tag selector and optional node property selection."),
        ],
    ) -> TagNodesResponse:
        """Return nodes attached to one OpenSVC Collector tag."""
        response = await core_get_tag_nodes(
            tag_id=request.tag_id,
            tag_name=request.tag_name,
            props=request.props,
            max_nodes=request.max_nodes,
        )
        return TagNodesResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="count_tag_nodes",
        description=(
            "Count OpenSVC Collector nodes attached to one tag selected "
            "by exact tag id or exact tag name. This uses a lightweight "
            "Collector count read from /tags/<id>/nodes."
        ),
        tags={"tags", "nodes", "count", "read"},
        annotations={
            "title": "Count OpenSVC Tag Nodes",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def count_tag_nodes(
        request: Annotated[
            TagIdentityRequest,
            Field(description="Tag selector used to count attached nodes."),
        ],
    ) -> TagRelationCountResponse:
        """Return the number of nodes attached to one tag."""
        response = await core_count_tag_nodes(
            tag_id=request.tag_id,
            tag_name=request.tag_name,
        )
        return TagRelationCountResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_tag_services",
        description=(
            "Return all OpenSVC Collector services attached to one tag "
            "selected by exact tag id or exact tag name. The tool follows "
            "Collector pagination until complete or max_services is reached."
        ),
        tags={"tags", "services", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Tag Services",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_tag_services(
        request: Annotated[
            TagServicesRequest,
            Field(description="Tag selector and optional service property selection."),
        ],
    ) -> TagServicesResponse:
        """Return services attached to one OpenSVC Collector tag."""
        response = await core_get_tag_services(
            tag_id=request.tag_id,
            tag_name=request.tag_name,
            props=request.props,
            max_services=request.max_services,
        )
        return TagServicesResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="count_tag_services",
        description=(
            "Count unique OpenSVC Collector services attached to one tag "
            "selected by exact tag id or exact tag name. The tool reads "
            "svcname only and deduplicates Collector rows by service name."
        ),
        tags={"tags", "services", "count", "read"},
        annotations={
            "title": "Count OpenSVC Tag Services",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def count_tag_services(
        request: Annotated[
            CountTagServicesRequest,
            Field(description="Tag selector and bounded count scan limit."),
        ],
    ) -> TagRelationCountResponse:
        """Return the number of unique services attached to one tag."""
        response = await core_count_tag_services(
            tag_id=request.tag_id,
            tag_name=request.tag_name,
            max_services=request.max_services,
        )
        return TagRelationCountResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="list_tag_props",
        description=(
            "List available OpenSVC Collector tag properties. "
            "Use this before list_tags to choose valid props and exact-match "
            "filter names."
        ),
        tags={"tags", "inventory", "schema", "read"},
        annotations={
            "title": "List OpenSVC Tag Properties",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def list_tag_props() -> TagPropsResponse:
        """Return the available tag properties exposed by the Collector."""
        response = await core_list_tag_props()
        return TagPropsResponse.model_validate(response)

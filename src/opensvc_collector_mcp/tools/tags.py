from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from opensvc_collector_mcp.config import TOOL_TIMEOUT_SECONDS
from opensvc_collector_mcp.core.tags import (
    attach_tag_to_node as core_attach_tag_to_node,
    attach_tag_to_service as core_attach_tag_to_service,
    count_tag_nodes as core_count_tag_nodes,
    count_tag_services as core_count_tag_services,
    count_tags as core_count_tags,
    create_tag as core_create_tag,
    delete_tag as core_delete_tag,
    detach_tag_from_node as core_detach_tag_from_node,
    detach_tag_from_service as core_detach_tag_from_service,
    get_tag as core_get_tag,
    get_tag_nodes as core_get_tag_nodes,
    get_tag_services as core_get_tag_services,
    list_tag_props as core_list_tag_props,
    list_tags as core_list_tags,
)
from opensvc_collector_mcp.models.tags import (
    AttachTagToNodeRequest,
    AttachTagToNodeResponse,
    AttachTagToServiceRequest,
    AttachTagToServiceResponse,
    CountTagServicesRequest,
    CountTagsRequest,
    CountTagsResponse,
    CreateTagRequest,
    CreateTagResponse,
    DeleteTagRequest,
    DeleteTagResponse,
    DetachTagFromNodeRequest,
    DetachTagFromNodeResponse,
    DetachTagFromServiceRequest,
    DetachTagFromServiceResponse,
    ListTagsRequest,
    TagIdentityRequest,
    TagNodesRequest,
    TagNodesResponse,
    TagPageResponse,
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
            "Create one OpenSVC Collector tag. Collector validates the submitted tag "
            "properties and authorizes the request using the authenticated caller's "
            "Basic Auth credentials."
        ),
        tags={"tags", "create", "write:tags"},
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
        name="delete_tag",
        description=(
            "Delete one OpenSVC Collector tag selected by its stable tag_id, including "
            "its node and service attachments. Resolve a human-readable tag_name with "
            "get_tag before calling this tool. Collector authorizes the request using "
            "the authenticated caller's Basic Auth credentials."
        ),
        tags={"tags", "delete", "delete:tags"},
        annotations={
            "title": "Delete OpenSVC Tag",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": True,
            "openWorldHint": False,
        },
    )
    async def delete_tag(
        request: Annotated[
            DeleteTagRequest,
            Field(description="Tag deletion selector."),
        ],
    ) -> DeleteTagResponse:
        """Delete an OpenSVC Collector tag."""
        response = await core_delete_tag(
            tag_id=request.tag_id,
            tag_name=None,
        )
        return DeleteTagResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="attach_tag_to_node",
        description=(
            "Attach one tag selected by tag_id to one node selected by node_id or "
            "nodename. MCP resolves selectors and refuses missing or ambiguous targets. "
            "Collector authorizes the request using the authenticated caller's Basic "
            "Auth credentials."
        ),
        tags={"tags", "nodes", "attach", "write:tags"},
        annotations={
            "title": "Attach OpenSVC Tag To Node",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": False,
            "openWorldHint": False,
        },
    )
    async def attach_tag_to_node(
        request: Annotated[
            AttachTagToNodeRequest,
            Field(description="Tag and node selectors for the attachment to create."),
        ],
    ) -> AttachTagToNodeResponse:
        """Attach one OpenSVC Collector tag to one node."""
        response = await core_attach_tag_to_node(
            tag_id=request.tag_id,
            tag_name=None,
            node_id=request.node_id,
            nodename=request.nodename,
            tag_attach_data=request.tag_attach_data,
        )
        return AttachTagToNodeResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="attach_tag_to_service",
        description=(
            "Attach one tag selected by tag_id to one service selected by svc_id or "
            "svcname. MCP resolves selectors and refuses missing or ambiguous targets. "
            "Collector authorizes the request using the authenticated caller's Basic "
            "Auth credentials."
        ),
        tags={"tags", "services", "attach", "write:tags"},
        annotations={
            "title": "Attach OpenSVC Tag To Service",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": False,
            "openWorldHint": False,
        },
    )
    async def attach_tag_to_service(
        request: Annotated[
            AttachTagToServiceRequest,
            Field(
                description="Tag and service selectors for the attachment to create."
            ),
        ],
    ) -> AttachTagToServiceResponse:
        """Attach one OpenSVC Collector tag to one service."""
        response = await core_attach_tag_to_service(
            tag_id=request.tag_id,
            tag_name=None,
            svc_id=request.svc_id,
            svcname=request.svcname,
        )
        return AttachTagToServiceResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="detach_tag_from_node",
        description=(
            "Detach one tag selected by tag_id from one node selected by node_id or "
            "nodename. MCP resolves selectors and verifies that the relation exists. "
            "Collector authorizes the request using the authenticated caller's Basic "
            "Auth credentials."
        ),
        tags={"tags", "nodes", "detach", "write:tags"},
        annotations={
            "title": "Detach OpenSVC Tag From Node",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": True,
            "openWorldHint": False,
        },
    )
    async def detach_tag_from_node(
        request: Annotated[
            DetachTagFromNodeRequest,
            Field(description="Tag and node selectors for the attachment to remove."),
        ],
    ) -> DetachTagFromNodeResponse:
        """Detach one OpenSVC Collector tag from one node."""
        response = await core_detach_tag_from_node(
            tag_id=request.tag_id,
            tag_name=None,
            node_id=request.node_id,
            nodename=request.nodename,
        )
        return DetachTagFromNodeResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="detach_tag_from_service",
        description=(
            "Detach one tag selected by tag_id from one service selected by svc_id or "
            "svcname. MCP resolves selectors and verifies that the relation exists. "
            "Collector authorizes the request using the authenticated caller's Basic "
            "Auth credentials."
        ),
        tags={"tags", "services", "detach", "write:tags"},
        annotations={
            "title": "Detach OpenSVC Tag From Service",
            "readOnlyHint": False,
            "idempotentHint": False,
            "destructiveHint": True,
            "openWorldHint": False,
        },
    )
    async def detach_tag_from_service(
        request: Annotated[
            DetachTagFromServiceRequest,
            Field(
                description="Tag and service selectors for the attachment to remove."
            ),
        ],
    ) -> DetachTagFromServiceResponse:
        """Detach one OpenSVC Collector tag from one service."""
        response = await core_detach_tag_from_service(
            tag_id=request.tag_id,
            tag_name=None,
            svc_id=request.svc_id,
            svcname=request.svcname,
        )
        return DetachTagFromServiceResponse.model_validate(response)

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
    ) -> TagPageResponse:
        """Return OpenSVC Collector tags and their selected properties."""
        response = await core_list_tags(
            filters=request.merged_filters(),
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            limit=request.limit,
            offset=request.offset,
        )
        return TagPageResponse.model_validate(response)

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
            "Return one page of OpenSVC Collector nodes attached to one tag "
            "selected by exact tag id or exact tag name."
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
            filters=request.filters,
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            limit=request.limit,
            offset=request.offset,
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
            "Return one page of OpenSVC Collector service rows attached to one "
            "tag selected by exact tag id or exact tag name."
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
            filters=request.filters,
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            limit=request.limit,
            offset=request.offset,
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

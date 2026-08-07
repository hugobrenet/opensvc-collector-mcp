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
            "Create one OpenSVC Collector tag. Before calling, ask the user "
            "to repeat an exact confirmation phrase and include it in "
            "request.confirmation.phrase. "
            "Collector authorizes this request using the authenticated "
            "caller's Basic Auth credentials."
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
            "Delete one OpenSVC Collector tag. Destructive and tag_id-only. "
            "If the user gives a tag_name, first call get_tag to resolve exactly "
            "one tag and read its tag_id and tag_name. Do not ask for a delete "
            "confirmation before this resolution step. This also deletes "
            "Collector attachments to nodes and services. Then ask the user to "
            "repeat an exact phrase containing both resolved values, for example: "
            "DELETE tag <tag_id> <tag_name>. When the latest user message "
            "contains that phrase, call delete_tag with tag_id, confirm_tag_id, "
            "confirm_tag_name, and request.confirmation.phrase. Do not pass "
            "tag_name as an execution selector; use confirm_tag_name only for "
            "correlation. "
            "Collector authorizes this request using the authenticated "
            "caller's Basic Auth credentials."
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
            Field(description="Tag deletion selector and explicit confirmation."),
        ],
    ) -> DeleteTagResponse:
        """Delete an OpenSVC Collector tag after explicit id and name confirmation."""
        response = await core_delete_tag(
            tag_id=request.tag_id,
            tag_name=None,
            confirm_tag_id=request.confirm_tag_id,
            confirm_tag_name=request.confirm_tag_name,
        )
        return DeleteTagResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="attach_tag_to_node",
        description=(
            "Attach one OpenSVC Collector tag to one node. The tag selector is "
            "tag_id-only. If the user gives a tag_name, first call get_tag to "
            "resolve exactly one tag and read its tag_id and tag_name. Do not "
            "ask for confirmation before this tag resolution step. Select the "
            "node by exact node_id or exact nodename; MCP resolves nodename to "
            "a stable node_id and refuses missing or ambiguous matches. Then ask "
            "the user to repeat an exact phrase containing the resolved tag and "
            "node. When the latest user message contains that phrase, call "
            "attach_tag_to_node with tag_id, confirm_tag_id, confirm_tag_name, "
            "node selector fields, and request.confirmation.phrase. Do not pass "
            "tag_name as an execution selector; use confirm_tag_name only for "
            "correlation. "
            "Collector authorizes this request using the authenticated "
            "caller's Basic Auth credentials."
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
        """Attach one OpenSVC Collector tag to one node after confirmation."""
        response = await core_attach_tag_to_node(
            tag_id=request.tag_id,
            tag_name=None,
            confirm_tag_id=request.confirm_tag_id,
            confirm_tag_name=request.confirm_tag_name,
            node_id=request.node_id,
            nodename=request.nodename,
            tag_attach_data=request.tag_attach_data,
        )
        return AttachTagToNodeResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="attach_tag_to_service",
        description=(
            "Attach one OpenSVC Collector tag to one service. The tag selector "
            "is tag_id-only. If the user gives a tag_name, first call get_tag to "
            "resolve exactly one tag and read its tag_id and tag_name. Do not "
            "ask for confirmation before this tag resolution step. Select the "
            "service by exact svc_id or exact svcname; MCP resolves svcname to "
            "a stable svc_id and refuses missing or ambiguous matches. Then ask "
            "the user to repeat an exact phrase containing the resolved tag and "
            "service. When the latest user message contains that phrase, call "
            "attach_tag_to_service with tag_id, confirm_tag_id, confirm_tag_name, "
            "service selector fields, and request.confirmation.phrase. Do not "
            "pass tag_name as an execution selector; use confirm_tag_name only "
            "for correlation. "
            "Collector authorizes this request using the authenticated "
            "caller's Basic Auth credentials."
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
        """Attach one OpenSVC Collector tag to one service after confirmation."""
        response = await core_attach_tag_to_service(
            tag_id=request.tag_id,
            tag_name=None,
            confirm_tag_id=request.confirm_tag_id,
            confirm_tag_name=request.confirm_tag_name,
            svc_id=request.svc_id,
            svcname=request.svcname,
        )
        return AttachTagToServiceResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="detach_tag_from_node",
        description=(
            "Detach one OpenSVC Collector tag from one node. The tag selector "
            "is tag_id-only. If the user gives a tag_name, first call get_tag to "
            "resolve exactly one tag and read its tag_id and tag_name. Do not "
            "ask for confirmation before this tag resolution step. Select the "
            "node by exact node_id or exact nodename; MCP resolves nodename to "
            "a stable node_id and refuses missing or ambiguous matches. MCP "
            "confirms the existing tag-node relation before deleting it in "
            "Collector. Then ask the user to repeat an exact phrase containing "
            "the resolved tag and node. When the latest user message contains "
            "that phrase, call detach_tag_from_node with tag_id, confirm_tag_id, "
            "confirm_tag_name, node selector fields, and request.confirmation."
            "phrase. Do not pass tag_name as an execution selector; use "
            "confirm_tag_name only for correlation. "
            "Collector authorizes this request using the authenticated "
            "caller's Basic Auth credentials."
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
        """Detach one OpenSVC Collector tag from one node after confirmation."""
        response = await core_detach_tag_from_node(
            tag_id=request.tag_id,
            tag_name=None,
            confirm_tag_id=request.confirm_tag_id,
            confirm_tag_name=request.confirm_tag_name,
            node_id=request.node_id,
            nodename=request.nodename,
        )
        return DetachTagFromNodeResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="detach_tag_from_service",
        description=(
            "Detach one OpenSVC Collector tag from one service. The tag selector "
            "is tag_id-only. If the user gives a tag_name, first call get_tag to "
            "resolve exactly one tag and read its tag_id and tag_name. Do not "
            "ask for confirmation before this tag resolution step. Select the "
            "service by exact svc_id or exact svcname; MCP resolves svcname to "
            "a stable svc_id and refuses missing or ambiguous matches. MCP "
            "confirms the existing tag-service relation before deleting it in "
            "Collector. Then ask the user to repeat an exact phrase containing "
            "the resolved tag and service. When the latest user message contains "
            "that phrase, call detach_tag_from_service with tag_id, "
            "confirm_tag_id, confirm_tag_name, service selector fields, and "
            "request.confirmation.phrase. Do not pass tag_name as an execution "
            "selector; use confirm_tag_name only for correlation. "
            "Collector authorizes this request using the authenticated "
            "caller's Basic Auth credentials."
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
        """Detach one OpenSVC Collector tag from one service after confirmation."""
        response = await core_detach_tag_from_service(
            tag_id=request.tag_id,
            tag_name=None,
            confirm_tag_id=request.confirm_tag_id,
            confirm_tag_name=request.confirm_tag_name,
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

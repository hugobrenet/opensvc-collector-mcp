from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from opensvc_collector_mcp.config import TOOL_TIMEOUT_SECONDS
from opensvc_collector_mcp.core.users import (
    get_user as core_get_user,
    list_user_props as core_list_user_props,
    list_users as core_list_users,
    search_users_by_primary_group as core_search_users_by_primary_group,
)
from opensvc_collector_mcp.models.users import (
    GetUserRequest,
    ListUsersRequest,
    UserDetailResponse,
    UserPropsResponse,
    UserRowsResponse,
    UsersByPrimaryGroupRequest,
    UsersByPrimaryGroupResponse,
)


def register_users_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="list_users",
        description=(
            "List or search OpenSVC Collector users using exact-match filters, "
            "Collector search, pagination, ordering, and selectable props. "
            "Defaults to a compact user inventory view."
        ),
        tags={"users", "inventory", "read"},
        annotations={
            "title": "List OpenSVC Users",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def list_users(
        request: Annotated[
            ListUsersRequest,
            Field(description="Optional user listing parameters."),
        ] = ListUsersRequest(),
    ) -> UserRowsResponse:
        """Return OpenSVC Collector users and their selected properties."""
        response = await core_list_users(
            filters=request.merged_filters(),
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            limit=request.limit,
            offset=request.offset,
        )
        return UserRowsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_user",
        description=(
            "Return OpenSVC Collector details for one user selected by self, "
            "numeric Collector user id, or exact email address. Optionally include "
            "the user primary group and group memberships."
        ),
        tags={"users", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC User",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_user(
        request: Annotated[
            GetUserRequest,
            Field(
                description=(
                    "User selector and optional relation expansion. Use "
                    "include_primary_group and include_groups only when needed."
                ),
            ),
        ],
    ) -> UserDetailResponse:
        """Return one OpenSVC Collector user, with optional group details."""
        response = await core_get_user(
            user=request.user,
            props=request.props,
            include_primary_group=request.include_primary_group,
            include_groups=request.include_groups,
            group_props=request.group_props,
        )
        return UserDetailResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="list_user_props",
        description=(
            "List available OpenSVC Collector user properties. "
            "Use this before list_users to choose valid props and exact-match "
            "filter names."
        ),
        tags={"users", "inventory", "schema", "read"},
        annotations={
            "title": "List OpenSVC User Properties",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def list_user_props() -> UserPropsResponse:
        """Return the available user properties exposed by the Collector."""
        response = await core_list_user_props()
        return UserPropsResponse.model_validate(response)

    # Acceptable for this Collector size, around 100-150 users: this tool uses
    # one /users request plus one /users/<id>/primary_group request per user.
    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="search_users_by_primary_group",
        description=(
            "Return OpenSVC Collector users whose primary group role exactly "
            "matches the requested value. The tool uses only REST API calls: "
            "/users followed by /users/<id>/primary_group for scanned users."
        ),
        tags={"users", "groups", "search", "read"},
        annotations={
            "title": "Search Users By Primary Group",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def search_users_by_primary_group(
        request: Annotated[
            UsersByPrimaryGroupRequest,
            Field(
                description=(
                    "Primary group role plus optional user filters and scan bound. "
                    "Uses only OpenSVC Collector REST API GET endpoints."
                ),
            ),
        ],
    ) -> UsersByPrimaryGroupResponse:
        """Return users whose primary group role matches exactly."""
        response = await core_search_users_by_primary_group(
            primary_group=request.primary_group,
            filters=request.merged_filters(),
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            max_users=request.max_users,
        )
        return UsersByPrimaryGroupResponse.model_validate(response)

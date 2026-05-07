from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from opensvc_collector_mcp.config import TOOL_TIMEOUT_SECONDS
from opensvc_collector_mcp.core.users import (
    count_users as core_count_users,
    count_users_by_group as core_count_users_by_group,
    count_users_by_primary_group as core_count_users_by_primary_group,
    get_user as core_get_user,
    list_user_props as core_list_user_props,
    list_users as core_list_users,
    search_users_by_group as core_search_users_by_group,
    search_users_by_primary_group as core_search_users_by_primary_group,
)
from opensvc_collector_mcp.models.users import (
    CountUsersByGroupRequest,
    CountUsersByGroupResponse,
    CountUsersByPrimaryGroupRequest,
    CountUsersByPrimaryGroupResponse,
    CountUsersRequest,
    CountUsersResponse,
    GetUserRequest,
    ListUsersRequest,
    UserDetailResponse,
    UserPropsResponse,
    UserRowsResponse,
    UsersByGroupRequest,
    UsersByGroupResponse,
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
        name="count_users",
        description=(
            "Count OpenSVC Collector users matching exact-match user filters. "
            "Use this when only the number of matching users is needed."
        ),
        tags={"users", "inventory", "count", "read"},
        annotations={
            "title": "Count OpenSVC Users",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def count_users(
        request: Annotated[
            CountUsersRequest,
            Field(description="Exact-match filters used to count Collector users."),
        ] = CountUsersRequest(),
    ) -> CountUsersResponse:
        """Return the number of users matching the provided filters."""
        response = await core_count_users(
            filters=request.merged_filters(),
            search=request.search,
        )
        return CountUsersResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_user",
        description=(
            "Return OpenSVC Collector details for one user selected by self, "
            "numeric Collector user id, exact username, or exact email address. Optionally include "
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
    # one /users request plus one /users/<id>/groups request per user.
    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="count_users_by_group",
        description=(
            "Count OpenSVC Collector users who are member of the requested group "
            "role. Uses only REST API GET calls: /users followed by "
            "/users/<id>/groups for scanned users."
        ),
        tags={"users", "groups", "count", "read"},
        annotations={
            "title": "Count OpenSVC Users By Group",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def count_users_by_group(
        request: Annotated[
            CountUsersByGroupRequest,
            Field(description="Group role plus optional user filters and scan bound."),
        ],
    ) -> CountUsersByGroupResponse:
        """Return the number of users member of the requested group role."""
        response = await core_count_users_by_group(
            group=request.group,
            filters=request.merged_filters(),
            orderby=request.orderby,
            search=request.search,
            max_users=request.max_users,
        )
        return CountUsersByGroupResponse.model_validate(response)

    # Acceptable for this Collector size, around 100-150 users: this tool uses
    # one /users request plus one /users/<id>/groups request per user.
    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="search_users_by_group",
        description=(
            "Return OpenSVC Collector users who are member of the requested "
            "group role. The tool uses only REST API calls: /users followed "
            "by /users/<id>/groups for scanned users."
        ),
        tags={"users", "groups", "search", "read"},
        annotations={
            "title": "Search Users By Group",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def search_users_by_group(
        request: Annotated[
            UsersByGroupRequest,
            Field(
                description=(
                    "Group role plus optional user filters and scan bound. "
                    "Uses only OpenSVC Collector REST API GET endpoints."
                ),
            ),
        ],
    ) -> UsersByGroupResponse:
        """Return users who are member of the requested group role."""
        response = await core_search_users_by_group(
            group=request.group,
            filters=request.merged_filters(),
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            max_users=request.max_users,
        )
        return UsersByGroupResponse.model_validate(response)

    # Acceptable for this Collector size, around 100-150 users: this tool uses
    # one /users request plus one /users/<id>/primary_group request per user.
    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="count_users_by_primary_group",
        description=(
            "Count OpenSVC Collector users whose primary group role exactly "
            "matches the requested value. Uses only REST API GET calls: /users "
            "followed by /users/<id>/primary_group for scanned users."
        ),
        tags={"users", "groups", "count", "read"},
        annotations={
            "title": "Count OpenSVC Users By Primary Group",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def count_users_by_primary_group(
        request: Annotated[
            CountUsersByPrimaryGroupRequest,
            Field(description="Primary group role plus optional user filters and scan bound."),
        ],
    ) -> CountUsersByPrimaryGroupResponse:
        """Return the number of users whose primary group role matches exactly."""
        response = await core_count_users_by_primary_group(
            primary_group=request.primary_group,
            filters=request.merged_filters(),
            orderby=request.orderby,
            search=request.search,
            max_users=request.max_users,
        )
        return CountUsersByPrimaryGroupResponse.model_validate(response)

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

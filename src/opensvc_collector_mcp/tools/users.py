from fastmcp import FastMCP

from opensvc_collector_mcp.config import TOOL_TIMEOUT_SECONDS
from opensvc_collector_mcp.core.users import list_user_props as core_list_user_props
from opensvc_collector_mcp.models.users import UserPropsResponse


def register_users_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="list_user_props",
        description=(
            "List available OpenSVC Collector user properties. "
            "Use this before future user listing tools to choose valid props "
            "and exact-match filter names."
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

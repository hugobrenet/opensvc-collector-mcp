from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

from opensvc_collector_mcp.core.nodes_core import list_nodes as core_list_nodes


def register_nodes_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        name="list_nodes",
        description=(
            "List nodes from the OpenSVC Collector inventory. "
            "Use the optional props argument to limit the returned fields "
            "and reduce response size."
        ),
        tags={"nodes", "inventory", "read"},
        annotations={
            "title": "List OpenSVC Nodes",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    def list_nodes(
        props: Annotated[
            str | None,
            Field(
                default=None,
                description=(
                    "Comma-separated Collector node properties to include in the response, "
                    "for example 'nodename,status,asset_env,loc_city'. "
                    "If omitted, the Collector default field set is returned."
                ),
            ),
        ] = None,
    ) -> dict[str, Any]:
        """Return OpenSVC Collector nodes and their selected properties."""
        return core_list_nodes(props=props)

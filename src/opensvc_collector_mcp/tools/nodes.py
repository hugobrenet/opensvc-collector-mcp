from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

from opensvc_collector_mcp.core.nodes_core import (
    count_nodes as core_count_nodes,
    get_node as core_get_node,
    get_node_health as core_get_node_health,
    get_nodes_inventory_stats as core_get_nodes_inventory_stats,
    list_node_props as core_list_node_props,
    list_nodes as core_list_nodes,
    search_nodes as core_search_nodes,
)


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

    @mcp.tool(
        name="list_node_props",
        description=(
            "List available OpenSVC Collector node properties. "
            "Use this before list_nodes or search tools to choose valid props."
        ),
        tags={"nodes", "inventory", "schema", "read"},
        annotations={
            "title": "List OpenSVC Node Properties",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    def list_node_props() -> dict[str, Any]:
        """Return the available node properties exposed by the Collector."""
        return core_list_node_props()

    @mcp.tool(
        name="search_nodes",
        description=(
            "Search OpenSVC Collector nodes using exact-match inventory filters. "
            "Use nodename_contains for a case-insensitive nodename substring search."
        ),
        tags={"nodes", "inventory", "search", "read"},
        annotations={
            "title": "Search OpenSVC Nodes",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    def search_nodes(
        filters: Annotated[
            str | None,
            Field(
                default=None,
                description=(
                    "Comma-separated exact-match filters using node properties, "
                    "for example 'status=warn,loc_city=Paris,manufacturer=Dell'. "
                    "Use list_node_props to discover valid properties."
                ),
            ),
        ] = None,
        nodename_contains: Annotated[
            str | None,
            Field(
                default=None,
                description="Case-insensitive substring to find in nodenames.",
            ),
        ] = None,
        status: Annotated[
            str | None,
            Field(default=None, description="Exact node status, for example 'up' or 'down'."),
        ] = None,
        asset_env: Annotated[
            str | None,
            Field(default=None, description="Exact asset environment, for example 'prod'."),
        ] = None,
        node_env: Annotated[
            str | None,
            Field(default=None, description="Exact node environment, for example 'TST'."),
        ] = None,
        loc_city: Annotated[
            str | None,
            Field(default=None, description="Exact node city, for example 'Paris'."),
        ] = None,
        loc_country: Annotated[
            str | None,
            Field(default=None, description="Exact node country, for example 'FR'."),
        ] = None,
        team_responsible: Annotated[
            str | None,
            Field(default=None, description="Exact responsible team."),
        ] = None,
        app: Annotated[
            str | None,
            Field(default=None, description="Exact application name."),
        ] = None,
        os_name: Annotated[
            str | None,
            Field(default=None, description="Exact operating system name."),
        ] = None,
        props: Annotated[
            str | None,
            Field(
                default=None,
                description=(
                    "Comma-separated node properties to return. "
                    "Defaults to a compact inventory field set."
                ),
            ),
        ] = None,
        limit: Annotated[
            int,
            Field(default=20, ge=1, le=100, description="Maximum number of nodes to return."),
        ] = 20,
        offset: Annotated[
            int,
            Field(default=0, ge=0, description="Number of matching nodes to skip."),
        ] = 0,
        max_scan: Annotated[
            int,
            Field(
                default=5000,
                ge=1,
                le=50000,
                description=(
                    "Maximum candidate nodes to scan when using nodename_contains. "
                    "Exact filters are handled by the Collector."
                ),
            ),
        ] = 5000,
    ) -> dict[str, Any]:
        """Search nodes by common inventory fields."""
        return core_search_nodes(
            filters=filters,
            nodename_contains=nodename_contains,
            status=status,
            asset_env=asset_env,
            node_env=node_env,
            loc_city=loc_city,
            loc_country=loc_country,
            team_responsible=team_responsible,
            app=app,
            os_name=os_name,
            props=props,
            limit=limit,
            offset=offset,
            max_scan=max_scan,
        )

    @mcp.tool(
        name="count_nodes",
        description=(
            "Count OpenSVC Collector nodes matching exact-match inventory filters. "
            "Use this for questions like how many nodes are down, in prod, "
            "or warn in Paris."
        ),
        tags={"nodes", "inventory", "count", "read"},
        annotations={
            "title": "Count OpenSVC Nodes",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    def count_nodes(
        filters: Annotated[
            str | None,
            Field(
                default=None,
                description=(
                    "Comma-separated exact-match filters using node properties, "
                    "for example 'status=warn,loc_city=Paris,manufacturer=Dell'. "
                    "Use list_node_props to discover valid properties."
                ),
            ),
        ] = None,
        status: Annotated[
            str | None,
            Field(default=None, description="Exact node status, for example 'up' or 'down'."),
        ] = None,
        asset_env: Annotated[
            str | None,
            Field(default=None, description="Exact asset environment, for example 'prod'."),
        ] = None,
        node_env: Annotated[
            str | None,
            Field(default=None, description="Exact node environment, for example 'TST'."),
        ] = None,
        loc_city: Annotated[
            str | None,
            Field(default=None, description="Exact node city, for example 'Paris'."),
        ] = None,
        loc_country: Annotated[
            str | None,
            Field(default=None, description="Exact node country, for example 'FR'."),
        ] = None,
        team_responsible: Annotated[
            str | None,
            Field(default=None, description="Exact responsible team."),
        ] = None,
        app: Annotated[
            str | None,
            Field(default=None, description="Exact application name."),
        ] = None,
        os_name: Annotated[
            str | None,
            Field(default=None, description="Exact operating system name."),
        ] = None,
    ) -> dict[str, Any]:
        """Return the number of nodes matching the provided filters."""
        return core_count_nodes(
            filters=filters,
            status=status,
            asset_env=asset_env,
            node_env=node_env,
            loc_city=loc_city,
            loc_country=loc_country,
            team_responsible=team_responsible,
            app=app,
            os_name=os_name,
        )

    @mcp.tool(
        name="get_node",
        description=(
            "Return all available OpenSVC Collector information for one node. "
            "The node is selected by its exact nodename."
        ),
        tags={"nodes", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC Node",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    def get_node(
        nodename: Annotated[
            str,
            Field(
                min_length=1,
                description=(
                    "Exact OpenSVC Collector nodename to inspect, "
                ),
            ),
        ],
    ) -> dict[str, Any]:
        """Return all available properties for one OpenSVC Collector node."""
        return core_get_node(nodename=nodename)

    @mcp.tool(
        name="get_node_health",
        description=(
            "Return a health-oriented summary for one OpenSVC Collector node. "
            "The result interprets status, maintenance, frozen state, alert dates, "
            "and communication timestamps."
        ),
        tags={"nodes", "inventory", "health", "read"},
        annotations={
            "title": "Get OpenSVC Node Health",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    def get_node_health(
        nodename: Annotated[
            str,
            Field(
                min_length=1,
                description=(
                    "Exact OpenSVC Collector nodename to evaluate, "
                ),
            ),
        ],
    ) -> dict[str, Any]:
        """Return health signals and interpreted issues for one node."""
        return core_get_node_health(nodename=nodename)

    @mcp.tool(
        name="get_nodes_inventory_stats",
        description=(
            "Return aggregate counts over OpenSVC Collector nodes. "
            "Use this for questions about possible values or counts by status, "
            "asset_env, node_env, location, app, or operating system."
        ),
        tags={"nodes", "inventory", "stats", "read"},
        annotations={
            "title": "Get OpenSVC Nodes Inventory Stats",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    def get_nodes_inventory_stats(
        fields: Annotated[
            str | None,
            Field(
                default=None,
                description=(
                    "Comma-separated node properties to aggregate. "
                    "Defaults to status, asset_env, node_env, loc_city, "
                    "loc_country, app, and os_name."
                ),
            ),
        ] = None,
        page_size: Annotated[
            int,
            Field(
                default=1000,
                ge=1,
                le=5000,
                description="Number of nodes fetched per Collector request.",
            ),
        ] = 1000,
        max_nodes: Annotated[
            int,
            Field(
                default=200000,
                ge=1,
                le=500000,
                description="Maximum number of nodes to scan before returning partial stats.",
            ),
        ] = 200000,
    ) -> dict[str, Any]:
        """Return aggregate node inventory counts."""
        return core_get_nodes_inventory_stats(
            fields=fields,
            page_size=page_size,
            max_nodes=max_nodes,
        )

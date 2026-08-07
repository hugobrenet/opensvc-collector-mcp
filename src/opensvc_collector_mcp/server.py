from fastmcp import FastMCP
from fastmcp.server.transforms.search import BM25SearchTransform
import uvicorn
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from opensvc_collector_mcp.config import (
    MCP_HOST,
    MCP_PORT,
    MCP_TOOL_SEARCH_MAX_RESULTS,
)
from opensvc_collector_mcp.auth.basic import CollectorBasicAuthMiddleware
from opensvc_collector_mcp.middleware import ToolSchemaValidationErrorMiddleware
from opensvc_collector_mcp.tools.apps import register_apps_tools
from opensvc_collector_mcp.tools.arrays import register_arrays_tools
from opensvc_collector_mcp.tools.clusters import register_clusters_tools
from opensvc_collector_mcp.tools.compliance import register_compliance_tools
from opensvc_collector_mcp.tools.disks import register_disks_tools
from opensvc_collector_mcp.tools.nodes import register_nodes_tools
from opensvc_collector_mcp.tools.services import register_services_tools
from opensvc_collector_mcp.tools.tags import register_tags_tools
from opensvc_collector_mcp.tools.users import register_users_tools


SERVER_INSTRUCTIONS = (
    "This server exposes the OpenSVC Collector domain to MCP clients. "
    "Use search_tools with concise English domain keywords to find the right "
    "tool. Raw collection tools return one page with a pagination object and "
    "do not return Collector metadata. To continue a collection, call the "
    "same tool with the same limit, filters, search, props, and ordering, and "
    "set offset to pagination.next_offset. Stop when pagination.complete is "
    "true or next_offset is null; a full page is not proof that the collection "
    "is complete. Do not increase limit between page calls and do not infer a "
    "total from the current page. When a user concept does not map clearly to "
    "a Collector property or value, first use the domain property-discovery "
    "tool (for example list_node_props), then a compact filtered/sample page "
    "or a specialized statistics tool when available. Prefer count tools for "
    "counts and detail tools for one selected object instead of scanning every "
    "page."
)


def build_mcp(*, require_basic_auth: bool = True) -> FastMCP:
    server = FastMCP(
        name="OpenSVC Collector",
        instructions=SERVER_INSTRUCTIONS,
        transforms=[BM25SearchTransform(max_results=MCP_TOOL_SEARCH_MAX_RESULTS)],
    )

    @server.custom_route("/health", methods=["GET"])
    async def health_check(request: Request) -> PlainTextResponse:
        return PlainTextResponse("OK")

    register_nodes_tools(server)
    register_clusters_tools(server)
    register_apps_tools(server)
    register_arrays_tools(server)
    register_services_tools(server)
    register_compliance_tools(server)
    register_disks_tools(server)
    register_users_tools(server)
    register_tags_tools(server)

    if require_basic_auth:
        server.add_middleware(CollectorBasicAuthMiddleware())
    server.add_middleware(ToolSchemaValidationErrorMiddleware(server))

    return server


mcp = build_mcp()


def create_app():
    return mcp.http_app(transport="http", stateless_http=True)


def main() -> None:
    """Run the MCP server over HTTP with uvicorn."""
    uvicorn.run(
        create_app(),
        host=MCP_HOST,
        port=int(MCP_PORT),
    )


if __name__ == "__main__":
    main()

from fastmcp import FastMCP
from fastmcp.server.transforms.search import BM25SearchTransform
import uvicorn
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from opensvc_collector_mcp.config import MCP_PORT, MCP_TOOL_SEARCH_MAX_RESULTS
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


def build_mcp() -> FastMCP:
    server = FastMCP(
        name="OpenSVC Collector",
        instructions=(
            "This server exposes the OpenSVC Collector domain to MCP clients. "
            "Use search_tools with concise English domain keywords when looking "
            "for the right tool, then use the available tools to inspect server "
            "health and Collector data."
        ),
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

    server.add_middleware(ToolSchemaValidationErrorMiddleware(server))

    return server


mcp = build_mcp()


def create_app():
    return mcp.http_app(transport="http", stateless_http=True)


def main() -> None:
    """Run the MCP server over HTTP with uvicorn."""
    uvicorn.run(
        create_app(),
        host="127.0.0.1",
        port=int(MCP_PORT or "8001"),
    )


if __name__ == "__main__":
    main()

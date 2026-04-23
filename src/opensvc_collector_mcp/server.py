from fastmcp import FastMCP
import uvicorn
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from opensvc_collector_mcp.config import MCP_PORT
from opensvc_collector_mcp.tools.clusters import register_clusters_tools
from opensvc_collector_mcp.tools.nodes import register_nodes_tools


mcp = FastMCP(
    name="OpenSVC Collector",
    instructions=(
        "This server exposes the OpenSVC Collector domain to MCP clients. "
        "Use the available tools to inspect server health and Collector data."
    ),
)

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")


register_nodes_tools(mcp)
register_clusters_tools(mcp)


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

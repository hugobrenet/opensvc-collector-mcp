from fastmcp import FastMCP


mcp = FastMCP(
    name="OpenSVC Collector",
    instructions=(
        "This server exposes the OpenSVC Collector domain to MCP clients. "
        "Use the available tools to inspect server health and Collector data."
    ),
)


@mcp.tool
def ping() -> str:
    """Return a simple health response."""
    return "pong"


def main() -> None:
    """Run the MCP server over the default stdio transport."""
    mcp.run()


if __name__ == "__main__":
    main()

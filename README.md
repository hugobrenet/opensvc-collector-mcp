# opensvc-collector-mcp

MCP server for the OpenSVC Collector API, built with FastMCP.

## Base server

This repository currently contains the minimal FastMCP server base:

- pinned to `fastmcp==3.2.4`
- stdio entrypoint for MCP clients
- a `ping` tool for smoke testing

## Run

Install dependencies:

```bash
pip install -e .
```

Run the server directly:

```bash
python -m opensvc_collector_mcp.server
```

Or through FastMCP:

```bash
fastmcp run src/opensvc_collector_mcp/server.py:mcp
```

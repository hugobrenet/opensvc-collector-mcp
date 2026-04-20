# OpenSVC Collector MCP

> Give AI agents a clean, typed MCP interface to the OpenSVC Collector API.

`opensvc-collector-mcp` is a FastMCP server that exposes OpenSVC Collector data as MCP tools, so LLM clients can inspect infrastructure inventory through a controlled HTTP interface.

## What It Is

- MCP server built with `FastMCP`
- HTTP transport served directly with `uvicorn`
- custom health route: `/health`
- current tool surface: node inventory tools
- architecture split between:
  `tools/` for MCP tool definitions and
  `core/` for business logic

## Why It Exists

The goal is to make OpenSVC Collector usable by AI assistants and agents without forcing them to call the raw Collector API directly.

This repository is focused on:

- clear tool contracts for MCP clients
- predictable environment-based configuration
- separation between MCP surface and Collector-specific logic

## FastMCP

This project uses `FastMCP` as the server framework that exposes Python functions as MCP tools and serves them over HTTP.

If you are new to FastMCP, start with the official documentation:

- FastMCP : https://gofastmcp.com

## Current Structure

```text
src/opensvc_collector_mcp/
├── client.py          # generic Collector HTTP client helpers
├── config.py          # environment variables
├── core/
│   └── nodes_core.py  # business logic for nodes
├── tools/
│   └── nodes.py       # FastMCP tool definitions
└── server.py          # FastMCP app + uvicorn entrypoint
```

## Environment

Create a `.env` file with:

```env
OPENSVC_USER=your-opensvc-user
OPENSVC_PASSWORD=your-opensvc-password
OPENSVC_API_BASE_URL=https://your-collector-host/init/rest/api
MCP_PORT=8001
```

## Run

Activate the local virtualenv:

```bash
. ./venv/bin/activate
```

Start the server:

```bash
PYTHONPATH=src python -m opensvc_collector_mcp.server
```

The server listens on:

```text
http://127.0.0.1:8001
```

## Health Check

```bash
curl http://127.0.0.1:8001/health
```

Expected response:

```text
OK
```

## MCP Endpoint

The MCP HTTP endpoint is exposed at:

```text
http://127.0.0.1:8001/mcp
```

## Tool Documentation

Tool documentation is organized by Collector domain:

- [Node tools](docs/tools/nodes.md)

## Development Notes

- FastMCP version is pinned in this project
- tool definitions should stay in `tools/`
- Collector logic should stay in `core/`

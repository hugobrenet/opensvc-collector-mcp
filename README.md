# OpenSVC Collector MCP

> Give AI agents a clean, typed MCP interface to the OpenSVC Collector API.

`opensvc-collector-mcp` is a FastMCP server that exposes OpenSVC Collector data as MCP tools, so LLM clients can inspect infrastructure inventory, service state, and operational history through a controlled HTTP interface.

## What It Is

- MCP server built with `FastMCP`
- HTTP transport served with `uvicorn`
- custom health route: `/health`
- typed Pydantic input and output models for MCP tools
- OpenSVC Collector read-only tool surface for nodes, services, and clusters
- architecture split between:
  - `tools/` for MCP tool definitions
  - `core/` for Collector workflows and business logic
  - `models/` for typed request and response contracts

## Why It Exists

The goal is to make OpenSVC Collector usable by AI assistants and agents without forcing them to call the raw Collector API directly.

This repository is focused on:

- clear tool contracts for MCP clients
- predictable environment-based configuration
- read-only Collector access patterns
- pagination-safe Collector reads
- separation between MCP surface and Collector-specific logic

## FastMCP

This project uses `FastMCP` as the server framework that exposes Python functions as MCP tools and serves them over HTTP.

If you are new to FastMCP, start with the official documentation:

- FastMCP: https://gofastmcp.com

## Current Structure

```text
src/opensvc_collector_mcp/
|-- client.py          # generic Collector HTTP client helpers
|-- config.py          # environment variables
|-- core/              # Collector workflows and business logic
|   |-- clusters_core.py
|   |-- nodes_core.py
|   `-- services_core.py
|-- models/            # Pydantic request and response models
|   |-- clusters_model.py
|   |-- nodes_model.py
|   `-- services_model.py
|-- tools/             # FastMCP tool definitions
|   |-- clusters.py
|   |-- nodes.py
|   `-- services.py
`-- server.py          # FastMCP app + uvicorn entrypoint
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
- [Cluster tools](docs/tools/clusters.md)
- [Service tools](docs/tools/services.md)

## Tool Domains

The current tool surface covers:

- node inventory, health, tags, compliance, checks, disks, network, services, and cluster membership
- service inventory, search, tags, config, instances, nodes, resources, disks, storage HBAs and targets, checks, alerts, actions, status history, frozen state, and health
- cluster node membership

All tools are intended to be read-only against OpenSVC Collector.

## Development Notes

- FastMCP version is pinned in this project.
- Tool definitions should stay in `tools/`.
- Collector logic should stay in `core/`.
- Request and response contracts should stay in `models/`.
- User-facing tool documentation should stay in `docs/tools/`.
- New tools should be validated with compile checks, FastMCP registration, Ruff, and read-only Collector tests.

## Project Status

This project is currently in development. Feedback, issues, and contributions are welcome.

For questions or discussion, you can contact me on LinkedIn:

https://fr.linkedin.com/in/hugo-brenet-49b200202

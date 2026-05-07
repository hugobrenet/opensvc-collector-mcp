# OpenSVC Collector MCP

> Give AI agents a clean, typed MCP interface to the OpenSVC Collector API.

`opensvc-collector-mcp` is a FastMCP server that exposes OpenSVC Collector data as MCP tools, so LLM clients can inspect infrastructure inventory, service state, and operational history through a controlled HTTP interface.

## What It Is

- MCP server built with `FastMCP`
- HTTP transport served with `uvicorn`
- custom health route: `/health`
- typed Pydantic input and output models for MCP tools
- OpenSVC Collector read-only tool surface for nodes, services, clusters, compliance, users, tags, apps, arrays, and disks
- architecture split between:
  - `tools/` for MCP tool definitions
  - `core/` for Collector workflows and business logic
  - `models/` for typed request and response contracts

## Why It Exists

The goal is to make OpenSVC Collector usable by AI assistants and agents without forcing them to call the raw Collector API directly.

This repository is focused on:

- clear tool contracts for MCP clients
- predictable environment-based configuration
- BM25 tool discovery for large MCP catalogs
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
|   |-- apps/
|   |-- arrays/
|   |-- clusters/
|   |-- compliance/
|   |-- disks/
|   |-- nodes/
|   |-- services/
|   |-- tags/
|   `-- users/
|-- models/            # Pydantic request and response models
|   |-- apps/
|   |-- arrays/
|   |-- clusters/
|   |-- compliance/
|   |-- disks/
|   |-- nodes/
|   |-- services/
|   |-- tags/
|   `-- users/
|-- tools/             # FastMCP tool definitions
|   |-- apps.py
|   |-- arrays.py
|   |-- clusters.py
|   |-- compliance.py
|   |-- disks.py
|   |-- nodes.py
|   |-- services.py
|   |-- tags.py
|   `-- users.py
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

## Tool Discovery

BM25 tool search is enabled by default to avoid sending the full tool catalog to MCP clients. With the default configuration, `tools/list` exposes only:

- `search_tools` to find relevant tools from natural-language or keyword queries
- `call_tool` to execute a discovered tool by name

The full tool catalog remains registered and callable. The number of returned search results is defined by the `MCP_TOOL_SEARCH_MAX_RESULTS` constant in `config.py`; the current value is `10`.

## Tool Documentation

Tool documentation is organized by Collector domain:

- [Node tools](docs/tools/nodes.md)
- [Service tools](docs/tools/services.md)
- [Cluster tools](docs/tools/clusters.md)
- [Compliance tools](docs/tools/compliance.md)
- [Disk tools](docs/tools/disks.md)
- [User tools](docs/tools/users.md)
- [Tag tools](docs/tools/tags.md)
- [App tools](docs/tools/apps.md)
- [Array tools](docs/tools/arrays.md)

## Tool Domains

The current tool surface covers:

- node inventory, health, tags, compliance, checks, disks, network, services, and cluster membership
- service inventory, search, tags, config, instances, nodes, resources, disks, storage HBAs and targets, checks, alerts, actions, status history, frozen state, and health
- global disk inventory and disk detail lookup
- cluster node membership
- compliance modulesets, rulesets, status, logs, usage, candidates, publications, and responsibles
- user inventory, counts, user detail lookup, primary group lookup, and attached group lookup
- tag inventory, tag detail, tagged nodes, and tagged services
- application inventory, nodes, services, responsibles, publications, quotas, and responsibility check
- storage array inventory, diskgroups, quotas, proxies, targets, and counts

All tools are intended to be read-only against OpenSVC Collector.

## Tests

The project uses `pytest` with in-memory `FastMCP` clients for MCP tool tests.

Run the full local validation with:

```bash
./venv/bin/python -m pytest
./venv/bin/python -m compileall -q src/opensvc_collector_mcp tests
./venv/bin/python -m ruff check src/opensvc_collector_mcp docs tests
git diff --check
```

The current test suite includes:

- FastMCP tool registration
- core tests for nodes, services, disks, and users
- MCP tool tests for nodes, services, disks, and users

## Development Notes

- FastMCP version is pinned in this project.
- Tool definitions should stay in `tools/`.
- Collector logic should stay in `core/`.
- Request and response contracts should stay in `models/`.
- User-facing tool documentation should stay in `docs/tools/`.
- New tools should include focused unit tests for their core logic and MCP wrapper behavior.
- New tools should be validated with pytest, compile checks, FastMCP registration, Ruff, and read-only Collector tests.

## Project Status

This project is currently in development. Feedback, issues, and contributions are welcome.

For questions or discussion, you can contact me on LinkedIn:

https://fr.linkedin.com/in/hugo-brenet-49b200202

# CODEX

Local project notes for working on `opensvc-collector-mcp`.

## Project

- Repository: `opensvc-collector-mcp`
- Goal: build an MCP server for the OpenSVC Collector API
- Base server framework: `FastMCP`
- Current pinned package version: `fastmcp==3.2.4`

## Python Environment

- Use the local virtualenv: `./venv`
- Activate with:

```bash
. ./venv/bin/activate
```

- Python in the venv is Python `3.13`

## Local MCP Server

- Server entrypoint:
  `src/opensvc_collector_mcp/server.py`
- The server is served directly with `uvicorn.run()`
- FastMCP HTTP app path:
  `/mcp`
- Custom health route:
  `/health`

Current package layout:

- `src/opensvc_collector_mcp/config.py`
  environment variables and shared global configuration constants
- `src/opensvc_collector_mcp/client.py`
  generic Collector API GET helper
- `src/opensvc_collector_mcp/tools/`
  FastMCP tool definitions
- `src/opensvc_collector_mcp/core/`
  business logic, Collector request handling, and shared core helpers such as
  node id to nodename resolution
- `src/opensvc_collector_mcp/core/services/`
  service-domain business logic split by concern: inventory, resources,
  compliance, actions, tags, health, and storage
- `src/opensvc_collector_mcp/core/nodes/`
  node-domain business logic split by concern: inventory, tags, location,
  organization, hardware, OS, cluster, network, compliance, checks, storage,
  services, health, and stats
- `src/opensvc_collector_mcp/core/clusters/`
  cluster-domain business logic
- `src/opensvc_collector_mcp/core/compliance/`
  global compliance-domain business logic
- `src/opensvc_collector_mcp/models/services/`
  service-domain Pydantic contracts split with the same concern boundaries
- `src/opensvc_collector_mcp/models/nodes/`
  node-domain Pydantic contracts split with the same concern boundaries
- `src/opensvc_collector_mcp/models/clusters/`
  cluster-domain Pydantic contracts

Current MCP node tool surface:

- `list_node_props`
- `list_nodes`
- `search_nodes`
- `count_nodes`
- `get_node`
- `get_node_tags`
- `search_node_by_tag`
- `search_nodes_without_tag`
- `get_node_location`
- `get_node_organization`
- `get_node_hardware`
- `get_node_os`
- `get_node_network`
- `get_node_compliance`
- `get_node_checks`
- `get_node_disks`
- `get_node_cluster`
- `get_node_services`
- `get_node_health`
- `get_nodes_inventory_stats`

Current MCP cluster tool surface:

- `get_cluster_nodes`

Current MCP compliance tool surface:

- `list_compliance_modulesets`
- `get_compliance_moduleset`
- `get_compliance_moduleset_modules`
- `get_compliance_moduleset_nodes`
- `get_compliance_moduleset_candidate_nodes`
- `get_compliance_moduleset_services`
- `get_compliance_moduleset_candidate_services`
- `get_compliance_moduleset_usage`
- `get_compliance_moduleset_definition`

Current MCP service tool surface:

- `list_services`
- `list_service_props`
- `search_services`
- `count_services`
- `search_frozen_services`
- `get_service`
- `get_service_config`
- `get_service_health`
- `get_service_status_history`
- `get_service_instance_status_history`
- `get_service_instances`
- `get_service_nodes`
- `get_service_disks`
- `get_service_hbas`
- `get_service_targets`
- `get_service_resources`
- `get_service_compliance_status`
- `get_service_compliance_logs`
- `get_service_resource_status`
- `get_service_tags`
- `search_services_by_tag`
- `search_services_without_tag`
- `get_service_alerts`
- `get_service_checks`
- `get_service_actions`
- `get_service_unacknowledged_errors`

Tool implementation standard:

- Every new FastMCP tool should define an explicit `name`
- Every new FastMCP tool should define a clear `description`
- Use `tags` for domain grouping such as `nodes`, `services`, `inventory`, `read`
- Use MCP `annotations` when relevant, especially:
  `title`, `readOnlyHint`, `idempotentHint`, `destructiveHint`, `openWorldHint`
- Tool request parameters should use
  `Annotated[RequestModel, Field(description="...")]`.
- Parameter descriptions should explain both purpose and expected format
- Prefer descriptions that help an MCP client choose the tool correctly, not just descriptions of the Python implementation
- Treat this as the default standard for all future tools in this repository

Async implementation standard:

- All new MCP tools must be implemented as `async def`.
- Core functions called by tools should also be `async def` when they perform
  Collector I/O.
- Collector HTTP calls should go through the async `collector_get()` helper in
  `client.py`.
- Do not introduce blocking HTTP clients like `requests` in new tool paths.
- If a future tool needs multiple Collector calls, keep the implementation
  awaitable and consider concurrent calls with `asyncio.gather()` when the calls
  are independent.

Pydantic model standard:

- All new MCP tools should expose Pydantic request and response models.
- Do not expose raw `dict` or `list` contracts directly from tool signatures.
- Use one request model and one response model per tool by default, even when a
  request model currently only inherits from a shared base model.
- Node models live in:
  `src/opensvc_collector_mcp/models/nodes/`
- Service models live in:
  `src/opensvc_collector_mcp/models/services/`
- Cluster models live in:
  `src/opensvc_collector_mcp/models/clusters/`
- Prefer a single `request` model argument for complex tools.
- Return Pydantic response models from tool functions.
- Use shared base request models for common behavior such as filters, but expose
  domain/tool-specific model names in tool signatures.
- Raw Collector payloads may be handled in `client.py` and `core/`, but the MCP
  boundary in `tools/` should be typed with Pydantic models.
- Raw Collector rows can stay as `dict[str, Any]` fields inside response models
  when Collector properties are dynamic.
- If a tool has no arguments, either keep it argument-less or introduce an empty
  request model only if consistency is worth the extra schema noise.
- Keep model definitions in `src/opensvc_collector_mcp/models/`, grouped by
  domain. Large domains should use packages such as `models/nodes/` or
  `models/services/`.

Layering standard:

- `tools/`: MCP surface, Pydantic request/response models, `Annotated` request
  parameter descriptions, and calls into core.
- `core/`: business logic and Collector-specific behavior. Core may use simple
  Python types and raw Collector dicts.
- Service core code lives under `core/services/` by concern. Keep generic service
  helpers private to that package.
- Node core code lives under `core/nodes/` by concern. Keep generic node helpers
  private to that package.
- Cluster core code lives under `core/clusters/`.
- `models/`: Pydantic contracts for MCP tool input/output.
- `client.py`: async HTTP client helpers only.
- `docs/`: human-facing tool documentation by domain.

Shared configuration standard:

- Put shared global configuration values in `src/opensvc_collector_mcp/config.py`.
- This includes environment-derived settings and project-wide constants such as
  HTTP request timeouts or MCP tool timeouts.
- Avoid duplicating the same global constant in multiple `tools/`, `core/`, or
  `client.py` modules. Import it from `config.py` instead.

Collection retrieval standard for `*_core.py`:

- When a core function reads a Collector endpoint returning a collection, pick
  one of two explicit strategies:
  `safe_limit_zero` or `prefer_pagination`.
- `safe_limit_zero`:
  use one Collector call with `limit=0` only for object-like or small, stable
  collections whose cardinality is expected to stay bounded in practice.
- `prefer_pagination`:
  use internal `limit/offset` pagination for any collection whose size can grow
  significantly or is not reliably bounded.
- Do not assume a `/resource/<id>/subresource` endpoint is small only because
  it is attached to one object. Validate with real Collector data first.
- `limit=0` is the exception, not the default.
- Prefer centralizing pagination mechanics in `client.py` helpers and keep
  `core/` focused on choosing the strategy and shaping the domain response.

Error and production-readiness notes:

- Collector HTTP errors currently bubble up from `httpx`; before production use,
  add clean error mapping that does not expose credentials.
- TLS verification is currently disabled for the local lab. Before production
  use, add `OPENSVC_VERIFY_TLS` and/or `OPENSVC_CA_BUNDLE`.
- Add focused tests as the tool surface grows, especially for model validation,
  filter merging, `count_nodes`, `search_nodes`, `get_node_health`, and stats.

Post-implementation validation:

- Run focused `py_compile` checks on modified Python modules.
- Run `./venv/bin/ruff check src` after each implementation.
- Validate FastMCP tool registration when tool signatures or models changed.
- Run `git diff --check` before handing changes back.
- For Collector-backed tools, validate with read-only GET calls only and avoid
  writing real infrastructure identifiers into docs, examples, or tests.

Tool documentation:

- Keep `README.md` oriented toward project presentation, setup, and links
- Put detailed tool documentation under `docs/tools/`
- Current node tool docs:
  `docs/tools/nodes.md`
- Current service tool docs:
  `docs/tools/services.md`
- Current compliance tool docs:
  `docs/tools/compliance.md`
- If new Collector domains are added, prefer one focused doc per domain:
  `docs/tools/services.md`, `docs/tools/checks.md`, etc.

Node tool design decisions:

- Do not add wrapper tools like `get_nodes_by_status`,
  `get_nodes_by_env`, `get_nodes_by_location`, or `get_nodes_by_app`
  unless they add domain-specific logic beyond filtering.
- `search_nodes` lists matching rows.
- `count_nodes` returns one optimized count using Collector `meta.total`.
- `get_nodes_inventory_stats` returns distributions and possible values.
- `get_node` returns raw full node detail.
- `get_node_health` returns an interpreted health summary.
- `list_node_props` is the schema discovery tool for node properties.

Generic node filters:

- `search_nodes` and `count_nodes` support generic exact-match filters over
  Collector node properties.
- Filter format:

```json
{
  "request": {
    "filters": {
      "prop": "value"
    }
  }
}
```

- Discover valid props with `list_node_props`.
- Examples:

```text
status=warn
{"asset_env": "lab", "loc_city": "Lab City"}
{"manufacturer": "LabVendor", "loc_rack": "LAB-RACK-01"}
{"node_env": "LAB", "status": "down", "loc_country": "ZZ"}
```

- Shortcut arguments still exist for common props:

```text
status
asset_env
node_env
loc_city
loc_country
team_responsible
app
os_name
```

- Generic `filters` can be combined with shortcut arguments on the same request
  model.
- Filters are exact matches. For nodename substring search, use
  `nodename_contains` on `search_nodes`.
- The Collector supports multiple filters through repeated query parameters:

```text
filters=status=warn&filters=loc_city=LabCity
```

- `collector_get()` accepts either a dict or a sequence of key/value tuples so
  repeated query parameters can be sent.

Run locally:

```bash
. ./venv/bin/activate
PYTHONPATH=src python -m opensvc_collector_mcp.server
```

Health check:

```bash
curl http://127.0.0.1:8001/health
```

HTTP MCP curl example:

```bash
curl -sS -X POST http://127.0.0.1:8001/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"count_nodes","arguments":{"request":{"filters":{"asset_env":"lab","loc_country":"ZZ","loc_rack":"LAB-RACK-01"}}}}}'
```

Local workflow used during tool development:

1. Implement or adjust the tool.
2. Run compile check:

```bash
PYTHONPATH=src python -m compileall -q src
```

3. Test core logic directly with `PYTHONPATH=src python -c ...`.
4. Test in-memory FastMCP with `fastmcp.Client`.
5. Start server:

```bash
PYTHONPATH=src python -m opensvc_collector_mcp.server
```

6. Validate by `curl` against `http://127.0.0.1:8001/mcp`.
7. Stop the server before handing back if requested.

Server process lookup/stop:

```bash
ps -ef | grep 'python -m opensvc_collector_mcp.server' | grep -v grep
kill <pid>
```

## Dependencies

- Dependencies are tracked in `requirements.txt` using `pip freeze`
- After installing packages in `./venv`, regenerate with:

```bash
pip freeze > requirements.txt
```

Important runtime dependencies currently used by the code:

- `fastmcp`
- `httpx`
- `uvicorn`
- `python-dotenv`

## Environment Variables

The project currently expects these variables in `.env`:

- `OPENSVC_USER`
- `OPENSVC_PASSWORD`
- `OPENSVC_API_BASE_URL`
- `MCP_PORT`

## Important Notes

- `client.py` currently uses `verify=False` for local Collector TLS. This is
  acceptable for the local lab but should become configurable before production
  use.
- `pyproject.toml` declares `fastmcp==3.2.4` and `httpx==0.28.1`.
  Runtime imports also include `python-dotenv`, `uvicorn`, `starlette`, and
  `pydantic` through the current FastMCP stack. Review dependency declarations
  before packaging/release.

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

- Use `./venv/bin/python` for commands so the repo-local dependencies are used

## Local MCP Server

- Server entrypoint:
  `src/opensvc_collector_mcp/server.py`
- The server is served directly with `uvicorn.run()`
- FastMCP HTTP app path:
  `/mcp`
- Custom health route:
  `/health`
- BM25 tool search is always enabled. `tools/list` exposes `search_tools` and
  `call_tool`, while the full catalog remains registered and callable.
- MCP HTTP requests are protected by a native FastMCP Basic Auth middleware.
  Clients must send `Authorization: Basic ...`; the server validates those
  credentials against the Collector `GET /users/self` endpoint before handling
  the MCP request.
- MCP tool execution is also protected by `CollectorReadToolAuthorizationMiddleware`
  when Basic Auth is enabled. The middleware authorizes both direct tool calls
  and proxied `call_tool` targets: the target tool must be tagged `read`, and
  the authenticated Collector user must belong to `Everybody` or `Manager`.
- `search_tools` remains public after authentication. BM25 discovery is not
  filtered yet, by design, so clients can report "tool exists but is
  unauthorized" instead of incorrectly reporting "no tool exists".
- MCP tool calls emit structured JSON audit logs on stdout/stderr through the
  `opensvc_collector_mcp.audit` logger. Audit V1 is intentionally log-based,
  not database-persisted.
- Gateway propagates a request id to MCP tool calls so multiple MCP events from
  one AI prompt can be correlated.
- Collector user credentials are not loaded by the MCP server from `.env`.
  Validated Basic Auth credentials are stored in request context and reused by
  `client.py` for Collector API calls.

Current package layout:

- `src/opensvc_collector_mcp/config.py`
  environment variables and shared global configuration constants
- `src/opensvc_collector_mcp/client.py`
  Collector API GET helpers using request-scoped Basic Auth credentials
- `src/opensvc_collector_mcp/auth/context.py`
  request-scoped Collector Basic Auth credential context
- `src/opensvc_collector_mcp/auth/basic.py`
  FastMCP middleware for Collector Basic Auth validation
- `src/opensvc_collector_mcp/auth/rbac.py`
  pure RBAC policy helpers for MCP tool authorization
- `src/opensvc_collector_mcp/auth/middleware.py`
  FastMCP tool authorization middleware and tool argument validation error
  enrichment
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
- `src/opensvc_collector_mcp/core/disks/`
  global disk-domain business logic
- `src/opensvc_collector_mcp/core/users/`
  user-domain business logic
- `src/opensvc_collector_mcp/core/tags/`
  tag-domain business logic
- `src/opensvc_collector_mcp/core/apps/`
  app-domain business logic
- `src/opensvc_collector_mcp/core/arrays/`
  array-domain business logic
- `src/opensvc_collector_mcp/models/services/`
  service-domain Pydantic contracts split with the same concern boundaries
- `src/opensvc_collector_mcp/models/nodes/`
  node-domain Pydantic contracts split with the same concern boundaries
- `src/opensvc_collector_mcp/models/clusters/`
  cluster-domain Pydantic contracts
- `src/opensvc_collector_mcp/models/compliance/`
  compliance-domain Pydantic contracts
- `src/opensvc_collector_mcp/models/disks/`
  disk-domain Pydantic contracts
- `src/opensvc_collector_mcp/models/users/`
  user-domain Pydantic contracts
- `src/opensvc_collector_mcp/models/tags/`
  tag-domain Pydantic contracts
- `src/opensvc_collector_mcp/models/apps/`
  app-domain Pydantic contracts
- `src/opensvc_collector_mcp/models/arrays/`
  array-domain Pydantic contracts

Current MCP node tool surface:

- `list_node_props`
- `list_nodes`
- `count_nodes`
- `get_node`
- `get_node_tags`
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
- `list_compliance_rulesets`
- `get_compliance_status`
- `get_compliance_logs`
- `get_compliance_run_detail`
- `get_compliance_ruleset`
- `get_compliance_ruleset_usage`
- `get_compliance_ruleset_variables`
- `get_compliance_ruleset_variable`
- `get_compliance_ruleset_candidate_nodes`
- `get_compliance_ruleset_candidate_services`
- `get_compliance_ruleset_publications`
- `get_compliance_ruleset_responsibles`
- `get_compliance_moduleset`
- `get_compliance_moduleset_modules`
- `get_compliance_moduleset_nodes`
- `get_compliance_moduleset_candidate_nodes`
- `get_compliance_moduleset_services`
- `get_compliance_moduleset_candidate_services`
- `get_compliance_moduleset_publications`
- `get_compliance_moduleset_responsibles`
- `get_compliance_moduleset_usage`
- `get_compliance_moduleset_definition`

Current MCP array tool surface:

- `list_array_props`
- `list_arrays`
- `count_arrays`
- `get_array`
- `get_array_diskgroups`
- `get_array_diskgroup`
- `list_array_diskgroups`
- `get_array_diskgroup_quotas`
- `get_array_diskgroup_quota`
- `get_array_proxies`
- `get_array_targets`
- `count_array_diskgroups`

Current MCP app tool surface:

- `list_app_props`
- `list_apps`
- `count_apps`
- `get_app`
- `am_i_responsible_for_app`
- `get_app_nodes`
- `count_app_nodes`
- `get_app_services`
- `count_app_services`
- `get_app_responsibles`
- `get_app_publications`
- `get_app_quotas`

Current MCP tag tool surface:

- `list_tag_props`
- `list_tags`
- `count_tags`
- `get_tag`
- `get_tag_nodes`
- `count_tag_nodes`
- `get_tag_services`
- `count_tag_services`

Current MCP user tool surface:

- `list_user_props`
- `list_users`
- `count_users_by_primary_group`
- `count_users_by_group`
- `count_users`
- `get_user`
- `search_users_by_group`
- `search_users_by_primary_group`

Current MCP service tool surface:

- `list_services`
- `list_service_props`
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
- `get_service_alerts`
- `get_service_checks`
- `get_service_actions`
- `get_service_unacknowledged_errors`

Current MCP disk tool surface:

- `list_disk_props`
- `list_disks`
- `count_disks`
- `get_disk`

Tool discovery standard:

- The server always enables `BM25SearchTransform`.
- Search returns up to `MCP_TOOL_SEARCH_MAX_RESULTS` tools. This is a code
  constant in `config.py`, currently set to `10`.
- BM25 is lexical search, not semantic AI. Tool names, descriptions, parameter
  names, and parameter descriptions must contain the words an LLM is likely to
  search for.
- Prefer descriptions that mention domain intent and common user language such
  as summary, statistics, distribution, count, detail, relation, storage, group,
  tag, app, array, node, and service when relevant.
- For raw listing tools, mention the specialized aggregate/detail tool when the
  LLM should prefer it over scanning a collection.

Tool implementation standard:

- Every new FastMCP tool should define an explicit `name`
- Every new FastMCP tool should define a clear `description`
- Use `tags` for domain grouping such as `nodes`, `services`, `inventory`, `read`
- Use MCP `annotations` when relevant, especially:
  `title`, `readOnlyHint`, `idempotentHint`, `destructiveHint`, `openWorldHint`
- Tool request parameters should use
  `Annotated[RequestModel, Field(description="...")]`.
- Parameter descriptions should explain both purpose and expected format
- Parameter and field descriptions should document units such as MB, timestamps, and boolean meaning when the Collector field is ambiguous
- Response models should describe nested raw Collector objects when they are returned alongside flattened fields
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

## Testing Standard

- Tests live under `tests/` and use `pytest` plus `pytest-asyncio`.
- `tests/conftest.py` provides an in-memory FastMCP client fixture and Collector
  mock helpers.
- Core tests should mock `collector_get` or `collector_get_all` and assert the
  Collector path, query parameters, filters, pagination, and response shaping.
- Tool tests should call the MCP tool through the FastMCP client and monkeypatch
  the imported core function in `tools/<domain>.py`.
- For FastMCP tool tests, assert `result.structured_content` rather than
  relying on the typed `result.data` object.
- When adding a new tool, add at least one core test and one tool wiring test.
  Add more tests when the core logic performs resolution, pagination, joins,
  fallback lookups, or count/search behavior.
- Keep `tests/test_mcp_registration.py` aligned with the expected registered
  tool count whenever the public MCP surface changes. Registration checks should
  inspect the underlying catalog with
  `build_mcp(require_basic_auth=False)._list_tools()` when no HTTP Basic Auth
  context is needed; default listing checks should expect the synthetic BM25
  tools `search_tools` and `call_tool`.
- Avoid real infrastructure identifiers in tests. Use neutral synthetic values
  such as `NODE-ID`, `SERVICE-ID`, `DISK-ID`, `GROUP`, or `APP-ID`.

Shared configuration standard:

- Put shared global configuration values in `src/opensvc_collector_mcp/config.py`.
- This includes environment-derived settings and project-wide constants such as
  HTTP request timeouts or MCP tool timeouts.
- Avoid duplicating the same global constant in multiple `tools/`, `core/`, or
  `client.py` modules. Import it from `config.py` instead.

Collection and pagination standard:

- Raw Collector collection tools must expose the same public contract whenever
  the Collector endpoint supports it:
  `limit`, `offset`, `orderby`, `filters`, `search`, and `props`.
- The LLM is responsible for paginating raw collection tools by calling the same
  tool again with a higher `offset`. Do not hide full collection scans behind a
  listing tool.
- Object-detail tools should expose only the natural selector and optional
  `props`: use `id | name` when users are likely to know a name but the Collector
  endpoint requires an id. Resolve names to ids in `core/`, not in `tools/`.
- Relation tools such as `/<domain>/<id>/<relation>` are collection tools. They
  should expose `id | name` plus `limit`, `offset`, `orderby`, `filters`,
  `search`, and `props`.
- Internal pagination is allowed only for business tools that must reason across
  multiple Collector pages: id/name resolution, joins, summaries, diagnostics,
  or endpoints that cannot answer correctly with one raw page.
- Business tools using internal pagination must expose domain limits such as
  `max_items`, `max_logs`, `max_nodes`, or `include_details`, not technical
  transport controls. Keep the server work bounded and document what is scanned.
- Do not expose technical pagination controls in MCP request models: no
  `strategy`, no `page_size`, and no `limit_zero`. These are implementation
  details that belong in `core/` or `client.py` only.
- `collector_get_all` may remain as an internal helper for bounded business
  logic, but new raw listing/relation tools should prefer one Collector page per
  MCP call.

Error and production-readiness notes:

- `ToolSchemaValidationErrorMiddleware` enriches FastMCP tool argument
  `ValidationError`s with the called tool input schema so MCP clients can retry
  with the correct payload after a single error. Keep the enrichment scoped to
  `call[tool_name]` validation errors so internal Pydantic validation failures
  are not misreported as client argument errors.
- `CollectorReadToolAuthorizationMiddleware` is the execution-time RBAC guard
  for the current read-only tool surface. It returns a structured
  `Unauthorized tool` error containing the required tag, required groups, tool
  tags, and current Collector groups.
- Current read authorization is complete for authenticated users in
  `Everybody` or `Manager`. Revisit the tag-to-group policy when adding tools
  that perform Collector `POST`, `PUT`, `DELETE`, or action/exec calls.

Future write/action RBAC chantier:

- Public OpenSVC docs do not currently provide enough detail on Collector
  privilege groups. Treat the Collector code as the source of truth, especially
  `collector/init/models/auth.py::check_privilege()` and REST handlers under
  `collector/init/models/rest/`.
- Collector authorization model observed in code:
  - `auth_group.role` is the group/privilege name.
  - `auth_group.privilege` distinguishes privilege groups from organizational
    groups.
  - `Manager` is the global override in `check_privilege()`.
  - `primary_group` is for task assignment/message routing, not authorization.
  - `Everybody` is an organizational/publication group, not a write privilege.
- Before adding any MCP tool backed by Collector `POST`, `PUT`, `DELETE`, or
  action/exec endpoints, replace the read-only authorization guard with an
  explicit policy table mapping MCP tags to Collector privilege groups. Deny by
  default for unknown tags, missing tags, or mixed destructive intent.
- Keep Collector REST as the final object/data-level authority. MCP RBAC should
  decide whether a tool class may be attempted; Collector still enforces the
  actual endpoint permissions and object scope.

Proposed MCP tags and Collector groups:

```text
read                         -> authenticated user; current gate is Everybody or Manager
write:nodes                  -> NodeManager
delete:nodes                 -> NodeManager plus explicit destructive guard
exec:nodes                   -> NodeExec
write:apps                   -> AppManager
write:users                  -> UserManager
write:users:self             -> SelfManager or UserManager, and target user is current user
write:users:primary_group:self -> SelfManager or UserManager, and target user is current user
write:groups                 -> GroupManager
write:privilege_groups       -> Manager
write:compliance             -> CompManager
exec:compliance              -> CompExec
write:checks                 -> CheckManager
exec:checks                  -> CheckExec
write:context_checks         -> ContextCheckManager
write:storage                -> StorageManager
write:networks               -> NetworkManager
write:tags                   -> TagManager
write:dns                    -> DnsManager
operate:dns                  -> DnsOperator
write:reports                -> ReportsManager
write:charts                 -> ChartsManager
write:forms                  -> FormsManager
write:provisioning_templates -> ProvisioningManager
write:docker_registries      -> DockerRegistriesManager
push:docker_registries       -> DockerRegistriesPusher
write:alerts                 -> AlertsManager
write:obsolescence           -> ObsManager
upload:safe                  -> SafeUploader
write:scheduler              -> Manager
write:sysreport              -> Manager
write:replication            -> ReplicationManager
write:quotas                 -> QuotaManager
```

SelfManager notes:

- `SelfManager` is relevant but contextual. It should never authorize generic
  `write:users` operations by itself.
- Use `SelfManager` only for self-scoped tools where the MCP request target is
  proven to be the authenticated Collector user. Resolve the current user from
  `/users/self` and compare against the requested user id/email or require the
  request model to use `self`.
- Known Collector behavior: modifying another user requires `UserManager`;
  modifying the current user allows `UserManager` or `SelfManager`. The same
  pattern exists for setting/unsetting the current user primary group.
- Self-scoped MCP tools should have distinct names and tags, for example
  `update_my_user_profile` with `write:users:self`, instead of overloading a
  generic admin tool.

Safety rules for the first write/action wave:

- Do not start with `delete` or unrestricted `exec` tools.
- Prefer one narrow, reversible domain first, with tests for allowed, denied,
  Manager override, unknown tag, and Collector endpoint rejection.
- Destructive tools must require explicit destructive tags such as
  `delete:<domain>` and should add dry-run or confirmation conventions before
  live execution.
- Audit is mandatory for write/delete/exec attempts, including allowed, denied,
  Collector-rejected, and execution-error cases. Include request id, user,
  client tool, target tool, target object identifiers, required privileges,
  user groups, status, duration, and sanitized error details.
- Audit V1 logs one `mcp.tool_call` event for allowed, denied, and error cases.
  Current event fields:
  - `request_id`
  - `user`
  - `client_tool`
  - `target_tool`
  - `decision`
  - `reason`
  - `duration_ms`
  - `status`
  - `error_type`
  - `error_message`
  - `required_tag`
  - `required_groups`
  - `user_groups`
  - `tool_tags`
- Audit logs must stay sanitized: no passwords, no `Authorization` headers, no
  API keys, and no raw sensitive payloads.
- Audit V1 was validated from Docker/OpenSVC logs for:
  - successful `call_tool` target execution.
  - RBAC denied target execution.
  - target tool execution error with sanitized root error type/message.
- `CollectorBasicAuthMiddleware` validates `Authorization: Basic ...` against
  Collector `GET /users/self`. FastMCP filters the `authorization` header by
  default, so keep `get_http_headers(include={"authorization"})` when reading
  the header.
- Because the Basic Auth check is implemented as native FastMCP middleware,
  authentication failures are returned as MCP/JSON-RPC errors in the SSE stream
  rather than HTTP `401` responses.
- `client.py` must use the request-scoped Collector credentials set by
  `CollectorBasicAuthMiddleware`. Do not reintroduce `OPENSVC_USER` or
  `OPENSVC_PASSWORD` as server-side Collector credentials.
- For proxied calls through `call_tool`, malformed proxy arguments should return
  the `call_tool` schema, while invalid target-tool arguments should return the
  target tool schema. Keep tests for both paths.
- Collector HTTP errors currently bubble up from `httpx`; before production use,
  add clean error mapping that does not expose credentials.
- TLS verification is currently disabled for the local lab. This is acceptable
  for the intended sidecar topology where MCP runs in the Collector network
  namespace and calls Collector nginx at `https://127.0.0.1/init/rest/api`; the
  Basic Auth traffic stays on loopback and does not traverse a routed network.
  If MCP ever targets an external hostname/IP, enable certificate verification
  and add `OPENSVC_VERIFY_TLS` and/or `OPENSVC_CA_BUNDLE`.
- Keep focused tests growing with the tool surface. At minimum, each new tool
  should get core tests for Collector request construction/business logic and a
  FastMCP tool test for request/model wiring.

Post-implementation validation:

- Run focused pytest tests for the touched domain first.
- Run the full test suite with `./venv/bin/python -m pytest` before handing back.
- Run compile checks with `./venv/bin/python -m compileall -q src/opensvc_collector_mcp tests`.
- Run `./venv/bin/python -m ruff check src/opensvc_collector_mcp docs tests` after each implementation.
- Validate FastMCP tool registration when tool signatures or models changed.
- Run `git diff --check` before handing changes back.
- For Collector-backed tools, validate with read-only GET calls only and avoid
  writing real infrastructure identifiers into docs, examples, or tests.

Tool documentation:

- Keep `README.md` oriented toward project presentation, setup, and links
- Put detailed tool documentation under `docs/tools/`
- Current tool docs:
  `docs/tools/nodes.md`, `docs/tools/services.md`, `docs/tools/clusters.md`,
  `docs/tools/compliance.md`, `docs/tools/disks.md`, `docs/tools/users.md`,
  `docs/tools/tags.md`, `docs/tools/apps.md`, and `docs/tools/arrays.md`
- If new Collector domains are added, prefer one focused doc per domain:
  `docs/tools/<domain>.md`.

Node tool design decisions:

- Do not add wrapper tools like `get_nodes_by_status`,
  `get_nodes_by_env`, `get_nodes_by_location`, or `get_nodes_by_app`
  unless they add domain-specific logic beyond filtering.
- `list_nodes` lists rows and handles exact filters, Collector search, pagination, and bounded `nodename_contains` lookup.
- `count_nodes` returns one optimized count using Collector `meta.total`.
- `get_nodes_inventory_stats` returns distributions and possible values.
- `get_node` returns raw full node detail.
- `get_node_health` returns an interpreted health summary.
- `list_node_props` is the schema discovery tool for node properties.

Generic node filters:

- `list_nodes` and `count_nodes` support generic exact-match filters over
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
  `nodename_contains` on `list_nodes`.
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
2. Add or update focused core and tool tests.
3. Run focused tests for the touched domain, for example:

```bash
./venv/bin/python -m pytest tests/core/test_nodes.py tests/tools/test_nodes_tools.py -q
```

4. Run full validation:

```bash
./venv/bin/python -m pytest
./venv/bin/python -m compileall -q src/opensvc_collector_mcp tests
./venv/bin/python -m ruff check src/opensvc_collector_mcp docs tests
git diff --check
```

5. Start server when live MCP/curl validation is needed:

```bash
PYTHONPATH=src ./venv/bin/python -m opensvc_collector_mcp.server
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

Important development dependencies currently used by tests and validation:

- `pytest`
- `pytest-asyncio`
- `ruff`

## Environment Variables

The MCP server reads process environment variables only. It does not call
`load_dotenv()` and must not load Collector user credentials from `.env`.

Required/optional process environment:

- `OPENSVC_API_BASE_URL`
- `MCP_PORT`

For local tests, a shell may source `.env` before starting the server, but
`OPENSVC_USER` and `OPENSVC_PASSWORD` are only test client inputs used to build
the outgoing MCP `Authorization: Basic ...` header. They are not server
configuration.

## Important Notes

- `client.py` currently uses `verify=False` for local Collector TLS. This is
  justified only when `OPENSVC_API_BASE_URL` points to Collector nginx on
  loopback inside the shared Collector network namespace, for example
  `https://127.0.0.1/init/rest/api`. For any external Collector URL or routed
  network path, TLS verification must be enabled and CA trust configured.
- `pyproject.toml` declares `fastmcp==3.2.4` and `httpx==0.28.1`.
  Runtime imports also include `uvicorn`, `starlette`, and `pydantic` through
  the current FastMCP stack. Review dependency declarations before
  packaging/release.

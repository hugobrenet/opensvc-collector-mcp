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
- Tool tags are descriptive metadata only. Domain/action tags such as `nodes`,
  `create`, and `delete`, and effect tags such as `read`, `write:tags`,
  `delete:tags`, and `exec:nodes`, support discovery, documentation, external
  orchestration, and contract tests. They must never be used by MCP to authorize
  a tool call.
- The MCP server is a harness-only backend. Direct standalone MCP-client use is
  unsupported, and production network policy must expose `/mcp` only to the
  dedicated harness.
- The harness owns tool proposal, user approval, execution coordination, and
  interaction audit. MCP tools expose business arguments only. Do not add
  approval phrases, evidence fields, or duplicated correlation fields to tool
  request models.
- MCP HTTP requests are protected by a native FastMCP Basic Auth middleware.
  Clients must send `Authorization: Basic ...`; the server validates those
  credentials against the Collector `GET /users/self` endpoint before handling
  the MCP request.
- Collector is the sole authorization authority. Every tool reuses the validated
  request-scoped Basic Auth credentials for Collector API calls, and Collector
  decides whether the authenticated user may execute the endpoint. MCP does not
  load Collector groups or map tool tags to grants.
- `search_tools` remains available after authentication. BM25 discovery is not
  filtered by Collector grants; Collector evaluates authorization only when a
  discovered tool calls its API.
- MCP deliberately does not implement business or security audit. A dedicated
  external harness owns interaction audit, request correlation, approval
  evidence, and outcome recording. MCP keeps only framework/runtime logs.
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
- `src/opensvc_collector_mcp/middleware.py`
  FastMCP tool argument validation error enrichment
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

- `create_node`
- `delete_node`
- `freeze_node`
- `thaw_node`
- `run_node_checks`
- `collect_node_sysreport`
- `push_node_asset`
- `push_node_disks`
- `push_node_packages`
- `push_node_patches`
- `push_node_stats`
- `pull_node_config`
- `push_node_config`
- `update_node_compliance_modules`
- `update_node_opensvc_agent`
- `scan_node_scsi`
- `reboot_node`
- `shutdown_node`
- `schedule_node_reboot`
- `unschedule_node_reboot`
- `update_node_properties`
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

- `create_tag`
- `delete_tag`
- `attach_tag_to_node`
- `attach_tag_to_service`
- `detach_tag_from_node`
- `detach_tag_from_service`
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

Harness-only execution and approval boundary:

- MCP must be used only through the dedicated harness. Do not document or
  support direct standalone MCP-client execution.
- The harness separates tool proposal from execution. It presents the proposed
  tool name and business arguments, obtains the required user approval according
  to harness policy, and only then forwards the call.
- Proposal context, approval evidence, interaction audit, and outcome recording
  belong to the harness. They must not be represented in MCP request schemas or
  persisted by MCP.
- MCP tools expose only business parameters. Never add generic approval phrases,
  duplicated correlation values, or chat-message evidence fields.
- Effect tags and MCP annotations are stable metadata for harness risk policy,
  discovery, documentation, and contract tests. They are not local
  authorization controls.
- MCP remains responsible for typed input validation, deterministic target
  resolution, exact-id checks, existence checks, relation checks, safe request
  construction, and sanitized errors.
- Collector remains the sole authorization authority. Each Collector request
  uses the validated request-scoped Basic Auth credentials.
- When adding a state-changing tool, update
  `tests/test_mcp_registration.py`, domain core/tool tests, tool docs under
  `docs/tools/`, effect tags, and annotations.

State-changing tool schema standard:

- Request models contain only values needed to perform the business operation.
  Examples include `node_id`, `tag_id`, writable properties, duration, or the
  two sides of a relation.
- Existing-object operations should prefer stable Collector ids at the public
  MCP boundary. A harness or agent can use read-only tools to resolve a
  human-readable name before proposing the mutation.
- Core functions may accept additional business selectors for internal reuse,
  but public wrappers should expose the narrowest unambiguous contract.
- Technical implementation details, approval state, gateway state, audit state,
  and duplicate correlation values do not belong in Pydantic tool inputs.
- Keep exactly one effect classification tag on every tool: `read`,
  `write:<domain>`, `delete:<domain>`, or `exec:<domain>`.
- Keep MCP annotations accurate, especially `readOnlyHint`,
  `idempotentHint`, and `destructiveHint`.

Delete tool selector standard:

- Destructive tools execute Collector DELETE requests with stable identifiers
  whenever the domain provides them, for example `node_id` or `tag_id`.
- Public delete schemas must not expose ambiguous `id_or_name` strings.
  Resolve a user-facing name with a read-only tool first, reject zero or
  multiple matches, and pass the resolved stable id.
- Core delete logic must re-read or resolve the exact target immediately before
  DELETE and reject unknown, ambiguous, or non-exact identifiers.
- Human-readable attributes remain useful in read responses and harness
  summaries, but they are not duplicated in the final delete payload unless the
  Collector operation itself requires them.
- If a Collector endpoint supports deletion only by name, document the
  exception, require exact prior resolution, and keep the core target check
  immediately before mutation.

State-changing tool class standards:

- All state-changing tools need a clear effect tag, accurate MCP annotations,
  sanitized errors, business-only request models, and Collector as final
  authority.
- `POST create` tools expose the new object's business fields. Add a local
  existence check only when Collector behavior makes it necessary, such as
  `create_node`, whose endpoint otherwise behaves like an upsert.
- `PUT/PATCH/POST update` tools expose stable target identifiers and explicit
  writable fields. Do not expose arbitrary transport or control payloads.
- `DELETE` tools follow the stable-id and immediate target-resolution standard
  above.
- `attach/detach` tools expose the business selectors for both relation sides.
  Core resolves both sides to stable ids and verifies relation existence before
  destructive detach calls. Do not silently batch relation changes unless the
  tool name and schema are explicitly batch-oriented.
- `rename` tools are logical updates and should use a real Collector
  rename/update endpoint. Do not synthesize rename as
  create/copy/reattach/delete unless the tool explicitly models that migration.
- `exec` tools trigger runtime or operational actions. They must use dedicated
  `exec:<domain>` tags, explicit target resolution, narrow scope, and no
  implicit batch behavior. Add dry-run or preview support when Collector exposes
  it.
- Do not claim a state-changing operation is executable merely because a user
  requests it. The operation must exist in the registered MCP tool catalog.

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

Collector authorization standard:

- `CollectorBasicAuthMiddleware` must continue validating credentials with
  `GET /users/self` before MCP request handling.
- Every Collector API call must reuse those request-scoped credentials.
- Collector is the only authorization authority for endpoint grants and object
  scope. Do not add local group lookups, grant tables, or tag-based preflight
  authorization.
- Effect tags such as `read`, `write:<domain>`, `delete:<domain>`, and
  `exec:<domain>` are stable classification metadata for discovery,
  documentation, external orchestration, harness policy, and contract
  tests. They are not security controls.
- Treat Collector handlers as the source of truth for request behavior and
  payloads, but do not duplicate their authorization policy in MCP.

Audit responsibility:

- MCP does not own business/security audit and must not add an audit middleware,
  audit event model, or persistent audit sink.
- A dedicated external harness is responsible for interaction audit, request
  correlation, approval evidence, tool arguments, and outcomes.
- MCP and framework runtime logs must never include passwords, Authorization
  headers, API keys, or raw sensitive payloads.

Safety rules for the first write/action wave:

- Do not start with `delete` or unrestricted `exec` tools.
- Prefer one narrow, reversible domain first, with tests for effect tags,
  business request construction, and Collector endpoint rejection.
- Destructive tools must require explicit destructive tags such as
  `delete:<domain>` and should add dry-run support when Collector exposes it.
  The tag delete tool uses `delete:tags`, exposes `tag_id` only at execution
  time, and resolves that exact id immediately before calling
  `DELETE /tags/<tag_id>`.
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
- `delete_node` exposes only `node_id`. Resolve a nodename with `get_node`
  before proposing the delete. Core resolves the exact id immediately before
  `DELETE /nodes/<node_id>`.
- Mark node deletion with `destructiveHint=true` and `delete:nodes`;
  Collector cascades node deletion to related runtime and inventory rows.
- `create_node` exposes `nodename` and optional `properties`. It checks exact
  nodename absence because Collector otherwise behaves like an upsert. Reject
  `node_id` and `nodename` inside `properties`.
- `update_node_properties` exposes only `node_id` and `properties`. Core
  resolves the current nodename immediately before calling
  `POST /nodes/<nodename>`. Reject `node_id` and `nodename` inside
  `properties`.
- Mark node property updates with `destructiveHint=true`: they can overwrite
  existing Collector values.
- Existing-node write and exec tools expose only `node_id` plus operation-
  specific business values. Core helpers may accept `nodename` for internal
  reuse, while public MCP wrappers pass `nodename=None`.
- `snooze_node_notifications` exposes `node_id` and `duration`.
  `unsnooze_node_notifications` exposes only `node_id`. Both use
  `POST /nodes/<node_id>/snooze`, carry `write:nodes`, and are marked as
  non-destructive writes.
- `list_nodes` handles exact filters, Collector search, pagination, and bounded
  `nodename_contains` lookup.
- `count_nodes` returns one optimized count using Collector `meta.total`.
- `get_nodes_inventory_stats` returns distributions and possible values.
- `get_node` returns raw full node detail.
- `get_node_health` returns an interpreted health summary.
- `list_node_props` is the schema discovery tool for node properties.

Node state-changing tool TODO list:

- General rule: re-check the current Collector handler before implementation,
  expose only business parameters, add exactly one effect tag, keep annotations
  accurate, add core/tool/schema tests, and update domain documentation.
- [x] `snooze_node_notifications`
  - `POST /nodes/<id>/snooze` with a Collector duration string.
  - Public schema: `node_id`, `duration`.
  - Effect tag: `write:nodes`; `destructiveHint=false`.
- [x] `unsnooze_node_notifications`
  - `POST /nodes/<id>/snooze` without a duration.
  - Public schema: `node_id`.
  - Separate from snooze so omitting duration cannot silently invert intent.
- [x] `attach_tag_to_node`
  - `POST /tags/<tag_id>/nodes/<node_id>`.
  - Public tag selector: `tag_id`; node selectors are `node_id`,
    `nodename`, or both.
  - Core resolves both objects to stable ids and refuses missing, ambiguous, or
    inconsistent selectors.
  - Optional business value: `tag_attach_data`.
- [x] `attach_tag_to_service`
  - `POST /tags/<tag_id>/services/<svc_id>`.
  - Public tag selector: `tag_id`; service selectors are `svc_id`,
    `svcname`, or both.
  - Core resolves both objects to stable ids.
- [x] `detach_tag_from_node`
  - `DELETE /tags/<tag_id>/nodes/<node_id>`.
  - Same business selectors as attach.
  - Core re-reads and validates the exact relation before DELETE.
- [x] `detach_tag_from_service`
  - `DELETE /tags/<tag_id>/services/<svc_id>`.
  - Same business selectors as attach.
  - Core re-reads and validates the exact relation before DELETE.
- [x] `create_node`
  - `POST /nodes` after checking exact nodename absence.
  - Public schema: `nodename`, optional `properties`.
  - Effect tag: `write:nodes`; Collector remains final authority for defaults
    and payload validation.
- [ ] Node compliance attach/detach tools
  - Collector APIs:
    `POST/DELETE /nodes/<id>/compliance/modulesets/<id>` and
    `/nodes/<id>/compliance/rulesets/<id>`.
  - Defer to the compliance domain unless there is a strong node UX reason.
  - Likely effect tag: `write:compliance`; verify route ownership first.
- [ ] Additional node-only `/actions` tools
  - Collector API: `PUT /actions` with `node_id=<node_id>` and one action.
  - Reuse `_enqueue_node_action()` for simple node-only `exec:nodes`
    actions unless extra business payload or another effect domain is required.
  - Each public tool must be narrow, named after one Collector action, and
    expose `node_id` plus only action-specific business parameters.
  - Completed actions:
    `freeze_node`, `thaw_node`, `run_node_checks`,
    `collect_node_sysreport`, `push_node_asset`, `push_node_disks`,
    `push_node_packages`, `push_node_patches`, `push_node_stats`,
    `pull_node_config`, `push_node_config`,
    `update_node_compliance_modules`, `update_node_opensvc_agent`,
    `scan_node_scsi`, `reboot_node`, `shutdown_node`,
    `schedule_node_reboot`, `unschedule_node_reboot`,
    `rotate_node_root_password`, and `wake_node_on_lan`.
  - Do not mix service-instance actions into node-only tools.
  - Re-check Collector action handlers and command effects before adding another
    high-impact action. The harness owns any stronger approval UX.
- [ ] Node compliance exec tools
  - Collector API: `PUT /actions` with `node_id=<node_id>`, action
    `compliance_check` or `compliance_fix`, and `module`, `moduleset`, or
    `ruleset`.
  - Classification: `exec:compliance`, not `exec:nodes`.
  - Defer to the compliance domain unless there is a strong node UX reason.

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

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
- Non-RBAC action tags such as `create` and `delete` are descriptive discovery
  tags only. RBAC continues to use explicit authorization tags such as
  `write:tags` and `delete:tags`.
- State-changing tools must include the shared Pydantic field
  `request.confirmation.phrase` using `models/common.py::ToolConfirmation`. The
  assistant generates this phrase after resolving/summarizing the target action,
  asks the user to repeat it verbatim in a new message, and only then calls the
  tool with that exact phrase. This field is part of the MCP input schema so
  `search_tools` exposes it to the LLM. The field is a gateway/LLM safety gate;
  core functions should keep receiving only business arguments.
- MCP HTTP requests are protected by a native FastMCP Basic Auth middleware.
  Clients must send `Authorization: Basic ...`; the server validates those
  credentials against the Collector `GET /users/self` endpoint before handling
  the MCP request.
- MCP tool execution is also protected by `CollectorToolAuthorizationMiddleware`
  when Basic Auth is enabled. The middleware authorizes both direct tool calls
  and proxied `call_tool` targets from a deny-by-default tag-to-Collector-group
  policy in `auth/rbac.py`. Read tools use `read -> Everybody or Manager`;
  tag write/delete tools use `write:tags` or `delete:tags` -> `TagManager` or `Manager`.
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
- `src/opensvc_collector_mcp/models/common.py`
  shared Pydantic contracts used across domains, including
  `ToolConfirmation` for state-changing tool input schemas

Current MCP node tool surface:

- `create_node`
- `delete_node`
- `freeze_node`
- `thaw_node`
- `run_node_checks`
- `collect_node_sysreport`
- `push_node_asset`
- `push_node_disks`
- `push_node_stats`
- `pull_node_config`
- `push_node_config`
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

State-changing confirmation contract:

- Every MCP tool that creates, updates, deletes, executes, or otherwise changes
  Collector state must expose a required `request.confirmation.phrase` field
  using `models/common.py::ToolConfirmation`.
- This is a schema-level MCP contract. Because it is in the Pydantic input
  schema, `search_tools` returns it to the LLM together with the selected tool
  metadata.
- The MCP schema only requires a non-empty phrase. It intentionally does not
  hard-code a semantic phrase, node id, tag id, or other object-specific token.
  The LLM prompt and tool descriptions tell the assistant to generate a precise
  phrase after resolving and summarizing the target action.
- Gateway enforces the generic chat safety gate: when the proxied `call_tool`
  payload contains `request.confirmation.phrase`, the phrase must appear
  verbatim in the latest user message before the gateway forwards the call to
  MCP.
- Tool descriptions for state-changing tools must tell the assistant to ask the
  user to repeat the exact phrase before calling the tool. Include stable
  identifiers in the suggested phrase when available, for example `node_id`
  plus `nodename` for node deletion.
- Core functions should receive only business arguments. Do not pass
  `confirmation` into `core/` or Collector REST payloads; it is a gateway/LLM
  safety guard at the MCP boundary.
- Current state-changing tools using this contract:
  `create_tag`, `delete_tag`, `attach_tag_to_node`, `attach_tag_to_service`, `detach_tag_from_node`, `detach_tag_from_service`, `create_node`, `delete_node`, `freeze_node`, `thaw_node`, `run_node_checks`, `collect_node_sysreport`, `push_node_asset`, `push_node_disks`, `push_node_stats`, `pull_node_config`, `push_node_config`, `update_node_properties`, `snooze_node_notifications`, and `unsnooze_node_notifications`.
- When adding another state-changing tool, update:
  `tests/test_mcp_registration.py`, the domain tool tests, tool docs under
  `docs/tools/`, and the tool description/annotations.

Delete tool selector and confirmation standard:

- Destructive delete tools must execute the Collector DELETE with a stable
  Collector identifier whenever the domain has one, for example `node_id` or
  `tag_id`. If the user gives a human-readable name, the assistant must first
  resolve it with a read-only tool/helper, refuse zero or multiple matches, and
  only then ask for confirmation. Do not expose ambiguous `id_or_name` string
  fields for destructive tools.
- `delete_node` is intentionally stricter than the generic selector pattern:
  the final confirmed tool call is `node_id` only. Its schema does not expose
  `nodename` as an execution selector. If the user asks to delete `node00008`,
  first call `get_node`, read `node_id` and `nodename`, ask the user to repeat
  `DELETE node <node_id> <nodename>`, then call `delete_node` with
  `node_id=<resolved node_id>`, `confirm_node_id=<resolved node_id>`,
  `confirm_nodename=<resolved nodename>`, and `confirmation.phrase=<verbatim
  latest user phrase>`. Never call `delete_node` with `nodename`, and never use
  a nodename value as `node_id`.
- Human-readable attributes such as `nodename`, tag name, username, app name, or
  service path are correlation attributes. Use them for resolution, target
  summaries, and explicit confirmation. Do not treat a correlation attribute as a
  second selector just because it appears in the confirmation phrase.
- If the user asks to delete by name, the assistant should first resolve the name
  with read/search tools when possible. If zero or multiple candidates are found,
  do not delete; ask for clarification or present the candidate ids. If exactly
  one candidate is found, summarize it and ask for explicit confirmation
  including both the stable id and the human-readable correlation attribute.
- Delete request models should use explicit selector fields such as `node_id` /
  `nodename` or `tag_id` / `tag_name`, plus explicit confirmation/correlation
  fields such as `confirm_node_id`, `confirm_nodename`, `confirm_tag_id`, or
  `confirm_tag_name`. The selector fields choose the object to operate on; the
  confirmation fields prove the user confirmed the resolved snapshot. Avoid a
  generic field named only `id` when users may confuse it with a name.
- Delete core logic should resolve or re-read the target immediately before the
  DELETE call, execute the DELETE with the stable id, then verify the supplied
  confirmation fields match the resolved snapshot. Reject on mismatch to catch
  stale LLM context, renamed objects, or user copy/paste errors.
- If a Collector endpoint only supports deletion by name and no stable id exists,
  document that exception in the tool docs and keep a stricter guard: exact
  prior read resolution, exact confirmation phrase, and explicit correlation
  field matched against the resolved object.
- The confirmation phrase should include the stable id and correlation attribute
  whenever both exist. Example for node deletion:
  `DELETE node <node_id> <nodename>`. This full phrase is copied into
  `confirmation.phrase`; it does not mean both `node_id` and `nodename` selector
  fields should be filled.

State-changing tool class standards:

- All state-changing classes share the same baseline: explicit RBAC tag,
  `request.confirmation.phrase`, clear MCP annotations, structured audit,
  sanitized errors, and Collector as final authority.
- `POST create` tools create new Collector objects. They do not need a mandatory
  pre-check for object existence; let Collector return the conflict/error and
  propagate it cleanly. The assistant should still summarize the object to
  create and ask for confirmation before calling the tool. Use names naturally
  for new objects when the object does not have a stable id yet.
- `PUT/PATCH/POST update` tools modify existing Collector objects. Prefer stable
  ids as selectors when the Collector endpoint supports them. If the Collector
  endpoint requires a name selector, document the exception, resolve/summarize
  the target first, and include the human-readable selector in confirmation.
  Update request models should expose only writable fields, not arbitrary raw
  payloads.
- `DELETE` tools follow the stricter delete standard above: stable id selector
  when available, human-readable correlation attribute, pre-delete snapshot,
  exact confirmation fields, and no ambiguous `id_or_name` selector.
- `attach/detach` tools are state-changing relation updates. Resolve both sides
  before execution, for example source id/name and target id/name. The request
  model should expose exact selectors for both sides and core code should execute
  Collector calls with resolved stable ids whenever available. Non-destructive
  relation updates require `confirmation.phrase`; destructive or sensitive
  relation updates may add stronger `confirm_*` fields for the resolved snapshot.
  Do not silently batch relation changes unless the tool name and schema are
  explicitly batch-oriented.
- `rename` tools are logical updates and should be treated as sensitive. Prefer
  a real Collector rename/update endpoint. Do not synthesize rename as
  create/copy/reattach/delete unless the tool is explicitly designed for that
  migration, all required state-changing tools exist, every affected object is
  summarized, and the user confirms the full plan. Check destination conflicts
  only when it is needed for target disambiguation or user clarity; Collector
  remains final authority for conflicts.
- `exec` tools trigger runtime or operational actions through Collector, for
  example service start/stop/restart/switch, node actions, compliance runs,
  provisioning, scheduler actions, or any endpoint that asks an OpenSVC agent or
  backend worker to do operational work. They must use dedicated `exec:<domain>`
  RBAC tags, explicit target resolution, confirmation with stable identifiers
  when available, no implicit batch scope, and audit for accepted, denied,
  Collector-rejected, and failed executions. Add dry-run/preview support when
  Collector exposes it.
- Do not claim a state-changing operation is executable just because a user asks
  for it. The assistant must select real MCP tools returned by `search_tools`;
  if the needed tool class is missing, answer that the operation is unsupported
  by the current MCP surface and offer read-only analysis.

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
- `CollectorToolAuthorizationMiddleware` is the execution-time RBAC guard for
  the MCP tool surface. It returns a structured `Unauthorized tool` error
  containing the denial reason, required tag, required groups, authorization
  tags, tool tags, and current Collector groups.
- The generic RBAC policy is deny-by-default: missing authorization tags,
  unknown authorization tags, mixed authorization tags, and missing Collector
  groups are refused before tool execution. Read tools use
  `read -> Everybody or Manager`; tag write/delete tools use
  `write:tags` or `delete:tags` -> `TagManager or Manager`.

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
  action/exec endpoints, keep using the explicit policy table mapping MCP tags
  to Collector privilege groups. Deny by default for unknown tags, missing tags,
  or mixed destructive intent.
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
delete:tags                  -> TagManager plus explicit destructive confirmation
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
  live execution. The tag delete tool uses `delete:tags`, exposes `tag_id` only
  at execution time, requires prior `get_tag` resolution when the user gives a
  tag name, requires `confirm_tag_id` plus `confirm_tag_name`, and matches both
  against the resolved Collector tag before calling `DELETE /tags/<tag_id>`.
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
- `delete_node` is `node_id` only at execution time. If the user provides a nodename, the assistant must first resolve it with `get_node`; only after a single node snapshot is resolved should it ask for the exact confirmation phrase containing both resolved `node_id` and `nodename`. The final `delete_node` payload must include `node_id`, matching `confirm_node_id`, `confirm_nodename`, and `confirmation.phrase`; it must not include `nodename`. Core still deletes through `DELETE /nodes/<resolved node_id>` and verifies confirmation fields before sending DELETE.
- Mark node deletion with MCP `destructiveHint=true` and `delete:nodes`: Collector cascades node deletion to related runtime and inventory rows.
- `create_node` uses `POST /nodes` with explicit `nodename` and optional `properties`. It requires only `request.confirmation.phrase` as the safety gate, but first checks exact `nodename` absence because Collector otherwise behaves like an upsert. Its request schema must reject `node_id` and `nodename` inside `properties`; Collector can otherwise treat submitted ids/names as updates to existing nodes. Collector remains the authority for defaults, read-only fields, and payload validation.
- `update_node_properties` is `node_id` only at the MCP boundary. If the user provides a nodename, first resolve it with `get_node`; the final payload includes `node_id`, matching `confirm_node_id`, `confirm_nodename`, `properties`, and `confirmation.phrase`. The core resolves the node_id to the current nodename immediately before calling Collector because the Collector endpoint remains `POST /nodes/<nodename>`. The MCP request rejects `node_id` and `nodename` inside `properties`; use a dedicated rename flow later if renaming is needed.
- Mark node property updates with MCP `destructiveHint=true`: they are write operations on an existing node and can overwrite existing Collector values.
- Node write/exec tools that operate on an existing node should expose
  `node_id` only at the MCP boundary when the Collector operation can execute
  with `node_id`. If the user provides a nodename, the assistant must first
  resolve it with `get_node`, read `node_id` and `nodename`, ask for a phrase
  containing both values, then call the tool with `node_id`, matching
  `confirm_node_id`, `confirm_nodename`, and `confirmation.phrase`. Core helpers
  may stay compatible with `nodename` for internal reuse, but MCP wrappers should
  pass `nodename=None` for migrated tools.
- `snooze_node_notifications` and `unsnooze_node_notifications` use `POST /nodes/<node_id>/snooze`, require `write:nodes`, require `node_id`, `confirm_node_id`, `confirm_nodename`, and `confirmation.phrase`, and are marked non-destructive writes.
- `list_nodes` lists rows and handles exact filters, Collector search, pagination, and bounded `nodename_contains` lookup.
- `count_nodes` returns one optimized count using Collector `meta.total`.
- `get_nodes_inventory_stats` returns distributions and possible values.
- `get_node` returns raw full node detail.
- `get_node_health` returns an interpreted health summary.
- `list_node_props` is the schema discovery tool for node properties.

Node state-changing tool TODO list:

- General rule for every item below: before implementation, re-check the
  current Collector handler in `collector/init/models/rest/api_nodes.py`,
  `collector/init/models/rest/api_tags.py`, and `api_handlers.py`; verify the
  applicable state-changing rule from this `CODEX.md`; add
  `request.confirmation.phrase`; add RBAC tags; add core/tool/schema tests; add
  docs under `docs/tools/nodes.md` or `docs/tools/tags.md` depending on the
  public tool domain.
- [x] `snooze_node_notifications`
  - Collector API: `POST /nodes/<id>/snooze` with `duration`.
  - Classification: `POST update` on node metadata, not runtime exec.
  - RBAC: `write:nodes` (`NodeManager` or `Manager`).
  - Selector/confirmation: MCP schema is `node_id` only. If the user gives a
    nodename, first resolve it with `get_node`; then call with `node_id`,
    matching `confirm_node_id`, `confirm_nodename`, and `confirmation.phrase`.
  - Request shape: explicit duration string; Collector validates duration through `convert_duration()`.
  - Response: includes the resolved node snapshot, returned Collector response, duration, and selector metadata.
- [x] `unsnooze_node_notifications`
  - Collector API: `POST /nodes/<id>/snooze` without `duration`.
  - Separate tool from snooze so omission of `duration` cannot silently invert the operation.
  - Same RBAC and selector/confirmation as `snooze_node_notifications`.
- [x] `attach_tag_to_node`
  - Collector API: `POST /tags/<tag_id>/nodes/<node_id>`; the tool deliberately
    avoids bulk `POST /tags/nodes` for a single explicit relation.
  - Classification: non-destructive `attach` relation update.
  - RBAC: `write:tags` (`TagManager` or `Manager`) because the Collector route
    lives in the tags API. Do not mix `write:tags` and `write:nodes` on one tool
    because RBAC denies mixed auth tags.
  - Selector/confirmation: public MCP schema is `tag_id` only on the tag side.
    If the user gives a `tag_name`, first resolve it with `get_tag`; then call
    with `tag_id`, matching `confirm_tag_id`, `confirm_tag_name`, and
    `confirmation.phrase`. Do not pass `tag_name` as an execution selector. The
    node side still accepts `node_id`, exact `nodename`, or both; core resolves
    both sides to stable ids, refuses missing or ambiguous names, and verifies
    confirmation/id correlation before posting.
  - Optional payload: typed `tag_attach_data`, passed to Collector only when
    provided.
  - No implicit batch attach. Add a separate batch tool later only if it has an
    explicit batch schema and confirmation summary.
- [x] `attach_tag_to_service`
  - Collector API: `POST /tags/<tag_id>/services/<svc_id>`; the tool deliberately
    avoids bulk `POST /tags/services` for a single explicit relation.
  - Classification: non-destructive `attach` relation update.
  - RBAC matches `attach_tag_to_node`: `write:tags` (`TagManager` or `Manager`)
    because the Collector route lives in the tags API.
  - Selector/confirmation: public MCP schema is `tag_id` only on the tag side.
    If the user gives a `tag_name`, first resolve it with `get_tag`; then call
    with `tag_id`, matching `confirm_tag_id`, `confirm_tag_name`, and
    `confirmation.phrase`. Do not pass `tag_name` as an execution selector. The
    service side still accepts `svc_id`, exact `svcname`, or both; core resolves
    both sides to stable ids, refuses missing or ambiguous names, and verifies
    confirmation/id correlation before posting.
  - No implicit batch attach. Add a separate batch tool later only if it has an
    explicit batch schema and confirmation summary.
- [x] `detach_tag_from_node`
  - Collector API: `DELETE /tags/<tag_id>/nodes/<node_id>`.
  - Classification: destructive relation update, not deletion of the tag or
    node object.
  - RBAC matches `attach_tag_to_node`: `write:tags` (`TagManager` or `Manager`)
    because the Collector route lives in the tags API.
  - Selector/confirmation: public MCP schema is `tag_id` only on the tag side.
    If the user gives a `tag_name`, first resolve it with `get_tag`; then call
    with `tag_id`, matching `confirm_tag_id`, `confirm_tag_name`, and
    `confirmation.phrase`. Do not pass `tag_name` as an execution selector. The
    node side still accepts `node_id`, exact `nodename`, or both; core resolves
    both sides to stable ids, verifies confirmation/id correlation, re-reads the
    current tag-node relation through `GET /tags/<tag_id>/nodes` filtered by
    `node_id`, refuses missing or ambiguous relations, and executes DELETE with
    resolved `tag_id` and `node_id`.
- [x] `detach_tag_from_service`
  - Collector API: `DELETE /tags/<tag_id>/services/<svc_id>`.
  - Classification: destructive relation update, not deletion of the tag or
    service object.
  - RBAC matches `attach_tag_to_service`: `write:tags` (`TagManager` or
    `Manager`) because the Collector route lives in the tags API.
  - Selector/confirmation: public MCP schema is `tag_id` only on the tag side.
    If the user gives a `tag_name`, first resolve it with `get_tag`; then call
    with `tag_id`, matching `confirm_tag_id`, `confirm_tag_name`, and
    `confirmation.phrase`. Do not pass `tag_name` as an execution selector. The
    service side still accepts `svc_id`, exact `svcname`, or both; core resolves
    both sides to stable ids, verifies confirmation/id correlation, re-reads the
    current tag-service relation through `GET /tags/<tag_id>/services` filtered
    by `svc_id`, refuses missing or ambiguous relations, and executes DELETE
    with resolved `tag_id` and `svc_id`.
- [x] `create_node`
  - Collector API: `POST /nodes`.
  - MCP first checks exact `nodename` absence with `/nodes` before calling
    `POST /nodes`, because Collector otherwise behaves like an upsert. Collector
    remains the final authority for defaults and payload validation.
  - RBAC: `write:nodes`.
  - Confirmation: `request.confirmation.phrase` only; no delete-style
    `confirm_*` fields.
  - Request model: explicit `nodename`, optional `properties`; MCP refuses
    existing nodenames and lets Collector validate other non-delete errors such
    as read-only fields.
- [ ] Node compliance attach/detach tools
  - Collector APIs: `POST/DELETE /nodes/<id>/compliance/modulesets/<id>` and
    `/nodes/<id>/compliance/rulesets/<id>`.
  - Defer to the compliance domain unless there is a strong node UX reason.
    These relations influence what the OpenSVC agent checks/fixes later, so
    treat them as more sensitive than simple inventory metadata.
  - Likely RBAC: `write:compliance` or a dedicated compliance relation policy,
    not plain `write:nodes`, but confirm against Collector privilege checks
    before implementation.
- [ ] Node-only `/actions` tools
  - Collector API: `PUT /actions` with `node_id=<node_id>` and one action.
  - Completed node action tools are not kept in this TODO list. Current completed
    `/actions` node tools: `freeze_node`, `thaw_node`, `run_node_checks`,
    `collect_node_sysreport`, `push_node_asset`, `push_node_disks`,
    `push_node_stats`, `pull_node_config`, `push_node_config`.
  - Use the existing core helper `_enqueue_confirmed_node_action()` for simple
    node-only `exec:nodes` actions unless the action requires extra payload or a
    different RBAC domain.
  - Shared rule: each tool must be narrow and named after one Collector action,
    expose `node_id` only in the public MCP schema, require `confirm_node_id`,
    `confirm_nodename`, and `confirmation.phrase`, and enqueue with the resolved
    `node_id` only. If the user gives a nodename, first resolve it with
    `get_node`; do not expose `nodename` as a tool execution selector.
  - Do not mix service-instance actions here. Actions requiring `svc_id` belong
    to service-domain tools even when they also take `node_id`.

  Lower-risk remaining first pass:
  - [x] `push_node_disks` -> action `pushdisks`
  - [x] `push_node_stats` -> action `pushstats`
  - [x] `pull_node_config` -> action `pull`
  - [x] `push_node_config` -> action `push`

  Medium-risk package/compliance-data refresh actions:
  - [ ] `push_node_packages` -> action `pushpkg`
  - [ ] `push_node_patches` -> action `pushpatch`
  - [ ] `update_node_compliance_data` -> action `updatecomp`
  - [ ] `update_node_package_data` -> action `updatepkg`
  - [ ] `scan_node_scsi` -> action `scanscsi`

  Checkpoint before high-impact actions:
  - [ ] Re-read Collector `api_action_queue.py` and
    `action_menu/action_menu.py` for exact privilege checks and command effects.
  - [ ] Decide if high-impact tools need stronger UX than a simple confirmation
    phrase, for example an explicit danger summary or dedicated confirmation
    wording.
  - [ ] Confirm naming and descriptions with the user before implementation.
  - [ ] Live-test one lower-risk node action end to end before adding reboot,
    shutdown, password rotation, or wake-on-LAN tools.

  High-impact actions, deferred until after the checkpoint:
  - [ ] `reboot_node` -> action `reboot`
  - [ ] `schedule_node_reboot` -> action `schedule_reboot`
  - [ ] `unschedule_node_reboot` -> action `unschedule_reboot`
  - [ ] `shutdown_node` -> action `shutdown`
  - [ ] `rotate_node_root_password` -> action `rotate_root_pw`
  - [ ] `wake_node_on_lan` -> action `wol`
- [ ] Node compliance exec tools
  - Collector API: `PUT /actions` with `node_id=<node_id>`, action
    `compliance_check` or `compliance_fix`, and `module`, `moduleset`, or
    `ruleset`.
  - Classification: `exec:compliance` (`CompExec` or `Manager`), not plain
    `exec:nodes`, because `do_node_comp_action()` checks `CompExec`.
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

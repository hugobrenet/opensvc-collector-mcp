# Compliance Tools

This document describes OpenSVC Collector MCP tools for global compliance data.

Compliance business logic lives under `src/opensvc_collector_mcp/core/compliance/`.
Compliance Pydantic models live under `src/opensvc_collector_mcp/models/compliance/`.
MCP tool definitions live in `src/opensvc_collector_mcp/tools/compliance.py`.

## Tools

### `list_compliance_modulesets`

Returns compliance modulesets published to the requesting Collector user's groups.

Use exact filters on Collector moduleset fields, such as `modset_name` or `id`,
to narrow the result. Default output returns a compact moduleset inventory view:

```text
id,modset_name,modset_author,modset_updated
```

Example:

```json
{
  "request": {
    "search": "opensvc",
    "limit": 10
  }
}
```

Output fields:

```text
meta
data
```


### `list_compliance_rulesets`

Returns compliance rulesets published to the requesting Collector user's groups.

Use exact filters on Collector ruleset fields, such as `ruleset_name` or `id`,
to narrow the result. Default output returns a compact ruleset inventory view:

```text
id,ruleset_name,ruleset_type,ruleset_public
```

Example:

```json
{
  "request": {
    "search": "opensvc",
    "limit": 10
  }
}
```

Output fields:

```text
meta
data
```


### `get_compliance_status`

Returns current/latest global OpenSVC compliance status rows from Collector.
Use this tool for questions such as which compliance modules are currently OK or
NOK, optionally filtered by `run_module`, `run_status`, `node_id`, `svc_id`, or
`rset_md5`.

The tool reads:

```text
/compliance/status
```

Observed `run_status` values are `0` for OK and `1` for error/NOK. The response
is paginated with `limit` and `offset`, and `meta.total` tells the caller whether
more pages are available. By default `latest=true`, so the tool returns the
latest/current status page with newest rows first.

Run logs are hidden by default. Set `include_run_log_preview=true` for a bounded
diagnostic preview, or `include_run_log=true` only when the full log is explicitly
needed.

Example:

```json
{
  "request": {
    "run_status": 1,
    "include_run_log_preview": true,
    "run_log_max_chars": 500,
    "limit": 10,
    "offset": 0
  }
}
```

Output fields:

```text
meta
data
```


### `get_compliance_logs`

Returns historical global OpenSVC compliance run logs from Collector. Use this
tool when the user asks for compliance logs, run history, previous executions, or
past check details for a focused node or service. The tool requires `node_id` or
`svc_id` because global `/compliance/logs` queries are too expensive on the
Collector side. Use `get_compliance_status` first to identify the failing row and
its node or service id when needed.

The tool reads:

```text
/compliance/logs
```

The response is paginated with `limit` and `offset`, and `meta.total` tells the
caller whether more pages are available. By default `latest=false`, so `offset`
works for historical pagination while rows are still returned newest first via
`latest_first=true`. Set `latest=true` only to force the newest log page.

A bounded `run_log_preview` is included by default. Set `include_run_log=false`
to keep full logs hidden, or `include_run_log=true` only when the full raw log is
explicitly needed.

Example:

```json
{
  "request": {
    "node_id": "1c4e7e32-7814-4aa9-92f3-2b486ad41ec0",
    "run_status": 1,
    "run_module": "aits.nodes.opensvc",
    "include_run_log_preview": true,
    "run_log_max_chars": 1000,
    "limit": 20,
    "offset": 0
  }
}
```

Output fields:

```text
meta
data
```


### `get_compliance_run_detail`

Returns details for one compliance run selected by `run_id`. Use this after
`get_compliance_status` or `get_compliance_logs` when the user asks for the
complete detail of one listed run.

The tool reads one of these endpoints depending on `source`:

```text
/compliance/status/<run_id>
/compliance/logs/<run_id>
```

Use `source="status"` when the `run_id` comes from `get_compliance_status`, and
`source="logs"` when the `run_id` comes from `get_compliance_logs`. A bounded
`run_log_preview` is included by default. Set `include_run_log=true` only when
the full raw log is explicitly needed.

Example:

```json
{
  "request": {
    "source": "logs",
    "run_id": 65120347,
    "include_run_log_preview": true,
    "run_log_max_chars": 2000
  }
}
```

Output fields:

```text
run_id
meta
data
```


### `get_compliance_ruleset`

Returns one compliance ruleset selected by Collector ruleset id or exact
`ruleset_name`.

Use `ruleset_name` for natural human requests. Use `list_compliance_rulesets`
first when the exact name is unknown. Default output returns the same compact
ruleset properties as the listing tool.

Example:

```json
{
  "request": {
    "ruleset_name": "02-aits.nodes.opensvc.tags"
  }
}
```

Output fields:

```text
object_id
ruleset_name
meta
data
```


### `get_compliance_ruleset_usage`

Returns where one compliance ruleset is reused or referenced, selected by
Collector ruleset id or exact `ruleset_name`.

Use `ruleset_name` for natural human requests. The tool resolves the ruleset id
through `/compliance/rulesets`, then calls:

```text
/compliance/rulesets/<ruleset_id>/usage
```

The returned sections depend on Collector data. Common sections include
`modulesets`, `rulesets`, `nodes`, and `services`.

Example:

```json
{
  "request": {
    "ruleset_name": "02-aits.nodes.opensvc.tags"
  }
}
```

Output fields:

```text
object_id
ruleset_name
meta
data
```


### `get_compliance_ruleset_variables`

Returns variables attached to one compliance ruleset selected by Collector
ruleset id or exact `ruleset_name`.

Use `ruleset_name` for natural human requests. The tool resolves the ruleset id
through `/compliance/rulesets`, then calls:

```text
/compliance/rulesets/<ruleset_id>/variables
```

Variable values are hidden by default. Set `include_var_value=true` only when the
question requires the actual values. The tool follows the standard Collector
collection contract with `limit`, `offset`, `orderby`, `filters`, `search`, and
`props`.

Example:

```json
{
  "request": {
    "ruleset_name": "02-aits.nodes.opensvc.tags",
    "include_var_value": false,
    "limit": 20,
    "offset": 0
  }
}
```

Output fields:

```text
object_id
relation
ruleset_name
meta
data
```


### `get_compliance_ruleset_variable`

Returns one variable attached to one compliance ruleset, selected by Collector
ruleset id or exact `ruleset_name` and a `variable_id` returned by
`get_compliance_ruleset_variables`.

The tool resolves the ruleset id through `/compliance/rulesets`, then calls:

```text
/compliance/rulesets/<ruleset_id>/variables/<variable_id>
```

Variable values are hidden by default. Set `include_var_value=true` only when the
question requires the actual value.

Example:

```json
{
  "request": {
    "ruleset_name": "02-aits.nodes.opensvc.tags",
    "variable_id": 303,
    "include_var_value": false
  }
}
```

Output fields:

```text
object_id
ruleset_id
ruleset_name
meta
data
```


### `get_compliance_ruleset_candidate_nodes`

Returns candidate nodes eligible for one compliance ruleset selected by
Collector ruleset id or exact `ruleset_name`. This does not return directly
attached nodes.

Use `ruleset_name` for natural human requests. The tool resolves the ruleset id
through `/compliance/rulesets`, then calls:

```text
/compliance/rulesets/<ruleset_id>/candidate_nodes
```

The tool follows the standard Collector collection contract with `limit`,
`offset`, `orderby`, `filters`, `search`, and `props`. Use `offset` to request
the next page when `meta.total` is greater than the returned count.

Example:

```json
{
  "request": {
    "ruleset_name": "02-aits.nodes.opensvc.tags",
    "props": "node_id,nodename,app,node_env,status,updated",
    "limit": 20,
    "offset": 0
  }
}
```

Output fields:

```text
object_id
relation
ruleset_name
meta
data
```


### `get_compliance_ruleset_candidate_services`

Returns candidate services eligible for one compliance ruleset selected by
Collector ruleset id or exact `ruleset_name`. This does not return directly
attached services.

Use `ruleset_name` for natural human requests. The tool resolves the ruleset id
through `/compliance/rulesets`, then calls:

```text
/compliance/rulesets/<ruleset_id>/candidate_services
```

The tool follows the standard Collector collection contract with `limit`,
`offset`, `orderby`, `filters`, `search`, and `props`. Use `offset` to request
the next page when `meta.total` is greater than the returned count.

Example:

```json
{
  "request": {
    "ruleset_name": "02-aits.nodes.opensvc.tags",
    "props": "svc_id,svcname,svc_app,svc_env,svc_status,svc_availstatus,updated",
    "limit": 20,
    "offset": 0
  }
}
```

Output fields:

```text
object_id
relation
ruleset_name
meta
data
```


### `get_compliance_ruleset_publications`

Returns groups one compliance ruleset is published to, selected by Collector
ruleset id or exact `ruleset_name`. Use this to know which groups can see or use
a ruleset.

The tool resolves the ruleset id through `/compliance/rulesets`, then calls:

```text
/compliance/rulesets/<ruleset_id>/publications
```

Example:

```json
{
  "request": {
    "ruleset_name": "02-aits.nodes.opensvc.tags",
    "limit": 20,
    "offset": 0
  }
}
```

Output fields:

```text
object_id
relation
ruleset_name
meta
data
```


### `get_compliance_ruleset_responsibles`

Returns groups responsible for one compliance ruleset, selected by Collector
ruleset id or exact `ruleset_name`.

The tool resolves the ruleset id through `/compliance/rulesets`, then calls:

```text
/compliance/rulesets/<ruleset_id>/responsibles
```

Example:

```json
{
  "request": {
    "ruleset_name": "02-aits.nodes.opensvc.tags",
    "limit": 20,
    "offset": 0
  }
}
```

Output fields:

```text
object_id
relation
ruleset_name
meta
data
```


### `get_compliance_moduleset`

Returns one compliance moduleset selected by Collector moduleset id or exact moduleset name.

Use `modset_name` for natural human requests. Use `list_compliance_modulesets`
first when the exact name is unknown. Default output returns the same compact
moduleset properties as the listing tool.

Example:

```json
{
  "request": {
    "modset_name": "01-aits.nodes.opensvc"
  }
}
```

Output fields:

```text
object_id
modset_name
meta
data
```


### `get_compliance_moduleset_modules`

Returns modules declared in one compliance moduleset, selected by Collector
moduleset id or exact `modset_name`.

Use this when the question is about the concrete modules composing a moduleset.
The response is paginated and includes Collector metadata such as `total`,
`limit`, and `offset`.

Example:

```json
{
  "request": {
    "modset_name": "02-aits.nodes.opensvc.tags"
  }
}
```

Output fields:

```text
object_id
modset_name
relation
meta
data
```


### `get_compliance_moduleset_nodes`

Returns nodes directly attached to one compliance moduleset, selected by
Collector moduleset id or exact `modset_name`.

Use this when the question is about effective node attachments. This is distinct
from candidate nodes, which are eligible nodes according to Collector targeting
rules but not necessarily attached.

Example:

```json
{
  "request": {
    "modset_name": "02-aits.nodes.opensvc.tags"
  }
}
```

Output fields:

```text
object_id
modset_name
relation
meta
data
```


### `get_compliance_moduleset_services`

Returns services directly attached to one compliance moduleset, selected by
Collector moduleset id or exact `modset_name`.

Use this when the question is about effective service attachments. This is
distinct from candidate services, which are eligible services according to
Collector targeting rules but not necessarily attached.

Example:

```json
{
  "request": {
    "modset_name": "aits.outils.controlm"
  }
}
```

Output fields:

```text
object_id
modset_name
relation
meta
data
```


### `get_compliance_moduleset_publications`

Returns groups one compliance moduleset is published to, selected by Collector
moduleset id or exact `modset_name`.

Use this when the question is about who can see or use a moduleset, or which
groups have publication access.

Example:

```json
{
  "request": {
    "modset_name": "aits.outils.controlm"
  }
}
```

Output fields:

```text
object_id
modset_name
relation
meta
data
```


### `get_compliance_moduleset_responsibles`

Returns groups responsible for one compliance moduleset, selected by Collector
moduleset id or exact `modset_name`.

Use this when the question is about who can maintain or administer a moduleset,
or which groups are responsible for it.

Example:

```json
{
  "request": {
    "modset_name": "aits.outils.controlm"
  }
}
```

Output fields:

```text
object_id
modset_name
relation
meta
data
```


### `get_compliance_moduleset_candidate_services`

Returns services eligible or attachable to one compliance moduleset according to
Collector targeting rules, selected by Collector moduleset id or exact
`modset_name`.

Use this when the question is about services targeted by, concerned by, eligible
for, or candidates for a moduleset. This is distinct from direct service
attachments returned by `get_compliance_moduleset_services`.

Example:

```json
{
  "request": {
    "modset_name": "aits.outils.controlm"
  }
}
```

Output fields:

```text
object_id
modset_name
relation
meta
data
```


### `get_compliance_moduleset_candidate_nodes`

Returns nodes eligible or attachable to one compliance moduleset according to
Collector targeting rules, selected by Collector moduleset id or exact
`modset_name`.

Use this when the question is about nodes targeted by, concerned by, eligible
for, or candidates for a moduleset. This is distinct from direct node
attachments returned by `get_compliance_moduleset_nodes`.

Example:

```json
{
  "request": {
    "modset_name": "02-aits.nodes.opensvc.tags"
  }
}
```

Output fields:

```text
object_id
modset_name
relation
meta
data
```


### `get_compliance_moduleset_usage`

Returns where one compliance moduleset is reused or referenced, selected by
Collector moduleset id or exact `modset_name`.

Use this when the question is about impact or dependency analysis, for example
which modulesets reference a given moduleset. This does not return the moduleset
content itself; use `get_compliance_moduleset_definition` for that.

Example:

```json
{
  "request": {
    "modset_name": "02-aits.nodes.opensvc.tags"
  }
}
```

Output fields:

```text
object_id
modset_name
meta
data
```


### `get_compliance_moduleset_definition`

Returns the declarative definition/export of one compliance moduleset selected
by Collector moduleset id or exact `modset_name`.

Use this when the question is about the content of a moduleset: included modules,
rulesets, variables, filtersets, publications, responsibles, and dependencies.
Variable values are hidden by default because they can be large or sensitive; set
`include_variable_values` to `true` only when the detailed values are needed.

Example:

```json
{
  "request": {
    "modset_name": "02-aits.nodes.opensvc.tags"
  }
}
```

Output fields:

```text
object_id
modset_name
meta
definition
```

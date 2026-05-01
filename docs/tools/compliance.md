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

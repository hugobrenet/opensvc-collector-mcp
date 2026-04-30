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

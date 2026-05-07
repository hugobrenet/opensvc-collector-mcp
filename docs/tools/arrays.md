# Array Tools

This document describes the OpenSVC Collector MCP tools for storage array inventory.

Array business logic lives under `src/opensvc_collector_mcp/core/arrays/`.
Array Pydantic models live under `src/opensvc_collector_mcp/models/arrays/`.
MCP tool definitions live in `src/opensvc_collector_mcp/tools/arrays.py`.

## Tools

### `list_array_props`

Returns the storage array properties exposed by the Collector.

Use this before building generic filters for `list_arrays`, or before selecting
custom `props` for array rows. The raw Collector property names include the
`stor_array.` table prefix; the response also includes `array_props` without
that prefix.

Typical properties include:

```text
id
array_name
array_model
array_firmware
array_cache
array_level
array_comment
array_updated
```

Output fields:

```text
count
available_props
array_props
```

### `count_arrays`

Counts OpenSVC Collector storage arrays matching exact-match filters without
returning array rows. This uses `/arrays` collection metadata with `limit=1`.

Example:

```json
{
  "request": {
    "filters": {
      "array_model": "ARRAY-MODEL"
    }
  }
}
```

Output fields:

```text
count
filters
search
```

### `get_array`

Returns one OpenSVC Collector storage array selected by exact `array_name`
or Collector array row id. The Collector endpoint accepts both forms through
`/arrays/<id>`.

Example:

```json
{
  "request": {
    "array": "ARRAY-NAME",
    "props": "id,array_name,array_model,array_firmware,array_cache,array_level,array_updated"
  }
}
```

Output fields:

```text
meta
data
```

### `count_array_diskgroups`

Counts OpenSVC Collector diskgroups attached to one storage array selected by
exact `array_name` or Collector array row id. This uses `/arrays/<id>/diskgroups`
collection metadata with `limit=1`.

Example:

```json
{
  "request": {
    "array": "ARRAY-NAME"
  }
}
```

Output fields:

```text
array
count
meta
```

### `get_array_diskgroup`

Returns one OpenSVC Collector diskgroup attached to one storage array. The
array selector accepts exact `array_name` or Collector array row id, and the
diskgroup selector accepts exact `dg_name` or Collector diskgroup row id. The
tool calls `/arrays/<id>/diskgroups/<id>`.

Example:

```json
{
  "request": {
    "array": "ARRAY-NAME",
    "diskgroup": "DISKGROUP-NAME",
    "props": "id,array_id,dg_name,dg_size,dg_free,dg_used,dg_reserved,dg_updated"
  }
}
```

Output fields:

```text
array
diskgroup
meta
data
```

### `get_array_diskgroups`

Returns all diskgroups attached to one OpenSVC Collector storage array
selected by exact `array_name` or Collector array row id. The tool calls
`/arrays/<id>/diskgroups` and follows Collector pagination until
`meta.complete` is true or `max_diskgroups` is reached.

Default props:

```text
id,array_id,dg_name,dg_size,dg_free,dg_used,dg_reserved,dg_updated
```

Example:

```json
{
  "request": {
    "array": "ARRAY-NAME",
    "props": "id,array_id,dg_name,dg_size,dg_free,dg_used,dg_reserved,dg_updated",
    "max_diskgroups": 200000
  }
}
```

Output fields:

```text
array
meta
data
```

### `get_array_proxies`

Returns all proxy rows attached to one OpenSVC Collector storage array selected
by exact `array_name` or Collector array row id. The tool calls
`/arrays/<id>/proxies` and follows Collector pagination until `meta.complete`
is true or `max_proxies` is reached.

Default props:

```text
id,array_id,node_id
```

Example:

```json
{
  "request": {
    "array": "ARRAY-NAME",
    "props": "id,array_id,node_id",
    "max_proxies": 200000
  }
}
```

Output fields:

```text
array
meta
data
```

### `get_array_targets`

Returns all target id rows attached to one OpenSVC Collector storage array
selected by exact `array_name` or Collector array row id. The tool calls
`/arrays/<id>/targets` and follows Collector pagination until `meta.complete`
is true or `max_targets` is reached.

Default props:

```text
id,array_id,array_tgtid
```

Example:

```json
{
  "request": {
    "array": "ARRAY-NAME",
    "props": "id,array_id,array_tgtid",
    "max_targets": 200000
  }
}
```

Output fields:

```text
array
meta
data
```

### `list_arrays`

Lists one page of OpenSVC Collector storage arrays.

This tool follows the standard Collector collection contract: `limit`, `offset`,
`orderby`, `filters`, `search`, and `props`. Use `offset` to request the next
page. It is also the array search tool: use exact-match shortcut filters such as
`array_name`, `array_model`, `array_level`, or generic `filters` discovered
through `list_array_props`.

Default props:

```text
id,array_name,array_model,array_firmware,array_cache,array_level,array_comment,array_updated
```

Example:

```json
{
  "request": {
    "filters": {
      "array_name": "ARRAY-NAME"
    },
    "props": "id,array_name,array_model,array_firmware,array_cache,array_level,array_updated",
    "limit": 20,
    "offset": 0,
    "orderby": "array_name"
  }
}
```

Output fields:

```text
meta
data
```

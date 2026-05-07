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

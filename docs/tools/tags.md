# Tag Tools

This document describes the OpenSVC Collector MCP tools for tag inventory.

Tag business logic lives under `src/opensvc_collector_mcp/core/tags/`.
Tag Pydantic models live under `src/opensvc_collector_mcp/models/tags/`.
MCP tool definitions live in `src/opensvc_collector_mcp/tools/tags.py`.

## Tools


### `get_tag`

Returns one OpenSVC Collector tag selected by exact `tag_id` or exact
`tag_name`. If `tag_name` is provided, the tool resolves it through `/tags`
before calling `/tags/<id>`.

Example:

```json
{
  "request": {
    "tag_name": "tag_name",
    "props": "tag_id,tag_name,tag_exclude,tag_created"
  }
}
```

Output fields:

```text
meta
data
```

### `get_tag_nodes`

Returns all nodes attached to one OpenSVC Collector tag selected by exact
`tag_id` or exact `tag_name`. If `tag_name` is provided, the tool resolves
it through `/tags`, then calls `/tags/<id>/nodes` and follows Collector
pagination until `meta.complete` is true or `max_nodes` is reached.

This is the tag-domain mirror of `get_node_tags`: `get_node_tags` starts
from one node and returns its tags; `get_tag_nodes` starts from one tag and
returns its nodes.

Example:

```json
{
  "request": {
    "tag_name": "tag_name",
    "props": "nodename,status,asset_env,node_env",
    "max_nodes": 200000
  }
}
```

Output fields:

```text
tag_id
tag_name
tag
meta
data
```

### `get_tag_services`

Returns all services attached to one OpenSVC Collector tag selected by exact
`tag_id` or exact `tag_name`. If `tag_name` is provided, the tool resolves
it through `/tags`, then calls `/tags/<id>/services` and follows Collector
pagination until `meta.complete` is true or `max_services` is reached.

This is the tag-domain mirror of `get_service_tags`: `get_service_tags`
starts from one service and returns its tags; `get_tag_services` starts
from one tag and returns its services. Returned services are deduplicated
by `svcname`; `meta.raw_count` and `meta.duplicate_count` describe the raw
Collector rows.

Example:

```json
{
  "request": {
    "tag_name": "tag_name",
    "props": "svcname,svc_app,svc_env,svc_status",
    "max_services": 200000
  }
}
```

Output fields:

```text
tag_id
tag_name
tag
meta
data
```

### `list_tag_props`

Returns the tag properties exposed by the Collector.

Use this before building generic filters for `list_tags`, or before selecting
custom `props` for tag rows. The raw Collector property names include the
`tags.` table prefix; the response also includes `tag_props` without that prefix.

Typical properties include:

```text
tag_id
tag_name
tag_exclude
tag_created
tag_data
```

Output fields:

```text
count
available_props
tag_props
```

### `list_tags`

Lists one page of OpenSVC Collector tags.

This tool follows the standard Collector collection contract: `limit`, `offset`,
`orderby`, `filters`, `search`, and `props`. Use `offset` to request the next
page. It is also the tag search tool: use exact-match shortcut filters such as
`tag_name`, `tag_id`, `tag_exclude`, or generic `filters` discovered through
`list_tag_props`.

Default props:

```text
tag_id,tag_name,tag_exclude,tag_created
```

Example:

```json
{
  "request": {
    "filters": {
      "tag_name": "tag_name"
    },
    "props": "tag_id,tag_name,tag_exclude,tag_created",
    "limit": 20,
    "offset": 0,
    "orderby": "tag_name"
  }
}
```

Output fields:

```text
meta
data
```

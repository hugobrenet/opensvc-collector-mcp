# Tag Tools

This document describes the OpenSVC Collector MCP tools for tag inventory.

Tag business logic lives under `src/opensvc_collector_mcp/core/tags/`.
Tag Pydantic models live under `src/opensvc_collector_mcp/models/tags/`.
MCP tool definitions live in `src/opensvc_collector_mcp/tools/tags.py`.

## Tools



### `create_tag`

Creates one OpenSVC Collector tag through `POST /tags`. This is a write tool
and requires `write:tags`, authorized for Collector `TagManager` or `Manager`
users by MCP RBAC. The MCP `create` tag is descriptive for discovery only. It
accepts `tag_name` and optional `tag_data` and `tag_exclude` fields. Because
it changes Collector state, the request requires `confirmation.phrase`: the
assistant must summarize the tag creation, ask the user to repeat a concise
phrase verbatim, and set `confirmation.phrase` only after that phrase appears in
the latest user message.

Example:

```json
{
  "request": {
    "tag_name": "mcp-test-tag",
    "tag_data": "created by mcp",
    "confirmation": {
      "phrase": "CREATE tag mcp-test-tag"
    }
  }
}
```

Output fields:

```text
meta
data
info
```

### `delete_tag`

Deletes one OpenSVC Collector tag through `DELETE /tags/<id>`. This is a
destructive tool and requires `delete:tags`, authorized for Collector
`TagManager` or `Manager` users by MCP RBAC. The MCP `delete` tag is descriptive
for discovery only. Collector also removes the tag attachments to nodes and
services.

The deletion selector uses the shared `TagSelector` contract: provide exactly
one of `tag_id` or `tag_name`. If `tag_name` is provided, MCP resolves it with
an exact `/tags` filter, refuses zero matches, refuses duplicate matches, and
then calls Collector using the resolved `tag_id`. The tool always reads a tag
snapshot before deletion and requires `confirm_tag_id` to match the resolved
`tag_id` and `confirm_tag_name` to match the resolved `tag_name`; the DELETE
call is not sent if either confirmation does not match. Because this is
destructive, the assistant must generate a concise confirmation phrase
containing the exact resolved `tag_id` and `tag_name`, ask the user to repeat it
verbatim in a new message, and set `confirmation.phrase` only after that exact
phrase appears in the latest user message. The gateway blocks the proxied
`call_tool` before MCP execution if the phrase is missing from that latest
message.

Example:

```json
{
  "request": {
    "tag_name": "mcp-test-tag",
    "confirm_tag_id": "tag-1",
    "confirm_tag_name": "mcp-test-tag",
    "confirmation": {
      "phrase": "DELETE tag tag-1 mcp-test-tag"
    }
  }
}
```

Output fields:

```text
tag_id
tag_name
tag
deleted
collector_response
meta
```

### `attach_tag_to_node`

Attaches one OpenSVC Collector tag to one node through
`POST /tags/<tag_id>/nodes/<node_id>`. This is a state-changing,
non-destructive relation update and requires `write:tags`, authorized for
Collector `TagManager` or `Manager` users by MCP RBAC.

The request uses exact selectors on both sides. For the tag, provide `tag_id`,
`tag_name`, or both. For the node, provide `node_id`, `nodename`, or both. MCP
resolves names with exact Collector filters, refuses missing or ambiguous
matches, verifies `id + name` correlation when both are provided, and then calls
Collector with the resolved stable IDs.

Because this changes Collector state, the request requires
`confirmation.phrase`: the assistant must summarize the exact tag/node
attachment, ask the user to repeat a concise phrase verbatim, and set
`confirmation.phrase` only after that phrase appears in the latest user message.
`tag_attach_data` can be provided when Collector-side attach metadata is needed.

Example:

```json
{
  "request": {
    "tag_id": "tag-1",
    "tag_name": "mcp-test-tag",
    "node_id": "node-1",
    "nodename": "lab-node-01",
    "tag_attach_data": "scope=lab",
    "confirmation": {
      "phrase": "ATTACH tag tag-1 mcp-test-tag to node node-1 lab-node-01"
    }
  }
}
```

Output fields:

```text
tag_id
tag_name
tag
node_id
nodename
node
attached
tag_attach_data
collector_response
meta
```

### `count_tags`

Counts OpenSVC Collector tags matching exact-match tag filters. It reads
`meta.total` from `/tags` with `limit=1`, so it is intended for count-only
questions.

Example:

```json
{
  "request": {
    "filters": {
      "tag_name": "tag_name"
    }
  }
}
```

Output fields:

```text
count
filters
```

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

### `count_tag_nodes`

Counts nodes attached to one OpenSVC Collector tag selected by exact
`tag_id` or exact `tag_name`. It resolves `tag_name` through `/tags`, then
reads `meta.total` from `/tags/<id>/nodes` with `limit=1`.

Example:

```json
{
  "request": {
    "tag_name": "tag_name"
  }
}
```

Output fields:

```text
tag_id
tag_name
tag
count
meta
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

### `count_tag_services`

Counts unique services attached to one OpenSVC Collector tag selected by
exact `tag_id` or exact `tag_name`. It resolves `tag_name` through `/tags`,
then reads `/tags/<id>/services` with `props=svcname` and deduplicates by
`svcname`. The response also exposes `raw_count` and `duplicate_count`.

Example:

```json
{
  "request": {
    "tag_name": "tag_name",
    "max_services": 200000
  }
}
```

Output fields:

```text
tag_id
tag_name
tag
count
raw_count
duplicate_count
meta
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

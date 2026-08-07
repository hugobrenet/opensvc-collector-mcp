# Tag Tools

The tag domain exposes typed Collector tag inventory and relation tools.
Collector remains the final authority for payload validation, endpoint
authorization, and object scope.

This MCP server is supported only behind the dedicated harness. The harness owns
proposal, user approval, execution coordination, and audit. MCP schemas expose
business parameters only; tool tags and annotations remain descriptive metadata
for harness policy and discovery.

## State-changing tool contract

Tag mutations accept the stable Collector `tag_id` at the MCP boundary. Resolve
a human-readable `tag_name` first with the read-only `get_tag` tool. Core
logic resolves all supplied object selectors, refuses missing or ambiguous
matches, and uses stable ids for Collector writes.

### `create_tag`

Creates a tag with `POST /tags`.

Business input:

- `tag_name` (required)
- `tag_data` (optional)
- `tag_exclude` (optional)

```json
{
  "request": {
    "tag_name": "mcp-test-tag",
    "tag_data": "created by mcp"
  }
}
```

Tags: `tags`, `create`, `write:tags`.
Annotation: `destructiveHint=false`.

### `delete_tag`

Deletes one tag with `DELETE /tags/<tag_id>`. Collector also removes its node
and service attachments. The MCP request contains only `tag_id`.

```json
{
  "request": {
    "tag_id": "TAG-ID"
  }
}
```

Core resolves an exact tag snapshot immediately before deletion. Collector
authorizes the operation using the authenticated caller's credentials.

Tags: `tags`, `delete`, `delete:tags`.
Annotation: `destructiveHint=true`.

### `attach_tag_to_node`

Attaches one tag to one node through
`POST /tags/<tag_id>/nodes/<node_id>`.

Business input:

- `tag_id`
- `node_id`, `nodename`, or both correlated selectors
- optional `tag_attach_data`

```json
{
  "request": {
    "tag_id": "TAG-ID",
    "node_id": "NODE-ID",
    "tag_attach_data": "scope=lab"
  }
}
```

Core resolves both objects to stable ids and refuses ambiguous or inconsistent
selectors. Tags: `tags`, `nodes`, `attach`, `write:tags`.
Annotation: `destructiveHint=false`.

### `attach_tag_to_service`

Attaches one tag to one service through
`POST /tags/<tag_id>/services/<svc_id>`.

Business input:

- `tag_id`
- `svc_id`, `svcname`, or both correlated selectors

```json
{
  "request": {
    "tag_id": "TAG-ID",
    "svc_id": "SERVICE-ID"
  }
}
```

Core resolves both objects to stable ids and refuses ambiguous or inconsistent
selectors. Tags: `tags`, `services`, `attach`, `write:tags`.
Annotation: `destructiveHint=false`.

### `detach_tag_from_node`

Detaches one tag-node relation through
`DELETE /tags/<tag_id>/nodes/<node_id>`.

Business input:

- `tag_id`
- `node_id`, `nodename`, or both correlated selectors

Before DELETE, MCP verifies that exactly one matching relation currently exists.

```json
{
  "request": {
    "tag_id": "TAG-ID",
    "node_id": "NODE-ID"
  }
}
```

Tags: `tags`, `nodes`, `detach`, `write:tags`.
Annotation: `destructiveHint=true`.

### `detach_tag_from_service`

Detaches one tag-service relation through
`DELETE /tags/<tag_id>/services/<svc_id>`.

Business input:

- `tag_id`
- `svc_id`, `svcname`, or both correlated selectors

Before DELETE, MCP verifies that exactly one matching relation currently exists.

```json
{
  "request": {
    "tag_id": "TAG-ID",
    "svc_id": "SERVICE-ID"
  }
}
```

Tags: `tags`, `services`, `detach`, `write:tags`.
Annotation: `destructiveHint=true`.

## Read-only tools

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

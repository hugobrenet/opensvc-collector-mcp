# App Tools

This document describes the OpenSVC Collector MCP tools for application code inventory.

App business logic lives under `src/opensvc_collector_mcp/core/apps/`.
App Pydantic models live under `src/opensvc_collector_mcp/models/apps/`.
MCP tool definitions live in `src/opensvc_collector_mcp/tools/apps.py`.

## Tools

### `get_app`

Returns one OpenSVC Collector application code selected by exact `app`
code or Collector app row id. The Collector endpoint accepts both forms
through `/apps/<id>`.

Example:

```json
{
  "request": {
    "app": "APP-CODE",
    "props": "app,app_domain,app_team_ops,description,updated"
  }
}
```

Output fields:

```text
meta
data
```

### `get_app_nodes`

Returns all nodes attached to one OpenSVC Collector application code
selected by exact `app` code or Collector app row id. The tool calls
`/apps/<id>/nodes` and follows Collector pagination until `meta.complete`
is true or `max_nodes` is reached.

Example:

```json
{
  "request": {
    "app": "APP-CODE",
    "props": "nodename,status,asset_env,node_env,app",
    "max_nodes": 200000
  }
}
```

Output fields:

```text
app
meta
data
```

### `count_app_nodes`

Counts nodes attached to one OpenSVC Collector application code selected
by exact `app` code or Collector app row id. It reads `meta.total` from
`/apps/<id>/nodes` with `limit=1`.

Example:

```json
{
  "request": {
    "app": "APP-CODE"
  }
}
```

Output fields:

```text
app
count
meta
```

### `get_app_services`

Returns all services attached to one OpenSVC Collector application code
selected by exact `app` code or Collector app row id. The tool calls
`/apps/<id>/services` and follows Collector pagination until
`meta.complete` is true or `max_services` is reached.

Example:

```json
{
  "request": {
    "app": "APP-CODE",
    "props": "svcname,svc_app,svc_env,svc_status",
    "max_services": 200000
  }
}
```

Output fields:

```text
app
meta
data
```

### `count_app_services`

Counts services attached to one OpenSVC Collector application code selected
by exact `app` code or Collector app row id. It reads `meta.total` from
`/apps/<id>/services` with `limit=1`.

Example:

```json
{
  "request": {
    "app": "APP-CODE"
  }
}
```

Output fields:

```text
app
count
meta
```

### `list_app_props`

Returns the app properties exposed by the Collector.

Use this before building generic filters for `list_apps`, or before selecting
custom `props` for app rows. The raw Collector property names include the
`apps.` table prefix; the response also includes `app_props` without that prefix.

Typical properties include:

```text
app
app_domain
app_team_ops
description
updated
id
```

Output fields:

```text
count
available_props
app_props
```

### `count_apps`

Counts OpenSVC Collector application codes matching exact-match filters
without returning app rows. This uses `/apps` collection metadata with
`limit=1`.

Example:

```json
{
  "request": {
    "filters": {
      "app": "APP-CODE"
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

### `list_apps`

Lists one page of OpenSVC Collector application codes.

This tool follows the standard Collector collection contract: `limit`, `offset`,
`orderby`, `filters`, `search`, and `props`. Use `offset` to request the next
page. It is also the app search tool: use exact-match shortcut filters such as
`app`, `app_domain`, `app_team_ops`, or generic `filters` discovered through
`list_app_props`.

Default props:

```text
app,app_domain,app_team_ops,description,updated
```

Example:

```json
{
  "request": {
    "filters": {
      "app": "APP-CODE"
    },
    "props": "app,app_domain,app_team_ops,description,updated",
    "limit": 20,
    "offset": 0,
    "orderby": "app"
  }
}
```

Output fields:

```text
meta
data
```

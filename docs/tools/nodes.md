# Node Tools

This document describes the OpenSVC Collector MCP tools for node inventory.

Node business logic lives in `src/opensvc_collector_mcp/core/nodes_core.py`.
MCP tool definitions live in `src/opensvc_collector_mcp/tools/nodes.py`.

## Tools

### `list_node_props`

Returns the node properties exposed by the Collector.

Use this before building generic filters for `search_nodes` or `count_nodes`.

Typical properties include:

```text
nodename
status
asset_env
node_env
loc_city
loc_country
manufacturer
loc_rack
team_responsible
```

### `list_nodes`

Returns nodes from the OpenSVC Collector inventory.

Optional argument:

- `props`: comma-separated node properties to include in the response.

Example:

```json
{
  "props": "nodename,status,asset_env,loc_city"
}
```

### `search_nodes`

Searches nodes and returns matching rows.

Use this when the user asks to list nodes matching criteria.

Common arguments:

- `filters`: exact-match filters using node properties.
- `props`: comma-separated properties to return.
- `limit`: maximum number of rows to return.
- `offset`: number of matching rows to skip.
- `nodename_contains`: case-insensitive substring search on `nodename`.

Shortcut filter arguments are also available:

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

Example:

```json
{
  "request": {
    "filters": {
      "asset_env": "prod",
      "loc_country": "FR",
      "loc_rack": "A13"
    },
    "props": "nodename,status,asset_env,loc_country,loc_rack",
    "limit": 10
  }
}
```

### `count_nodes`

Counts nodes matching filters.

Use this when the user asks "how many nodes" match criteria.

This tool is optimized for count questions: it requests one row from the
Collector and reads `meta.total`.

Common argument:

- `filters`: exact-match filters using node properties.

Shortcut filter arguments are also available:

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

Example:

```json
{
  "request": {
    "filters": {
      "status": "warn",
      "loc_city": "Paris",
      "asset_env": "prod"
    }
  }
}
```

Typical response:

```json
{
  "count": 0,
  "filters": {
    "status": "warn",
    "loc_city": "Paris",
    "asset_env": "prod"
  }
}
```

### `get_node`

Returns all available Collector information for one node selected by exact
`nodename`.

Example:

```json
{
  "request": {
    "nodename": "lab-paris-01"
  }
}
```

### `get_node_health`

Returns a health-oriented summary for one node.

It interprets fields like:

```text
status
last_comm
updated
maintenance_end
node_frozen
hw_obs_warn_date
hw_obs_alert_date
os_obs_warn_date
os_obs_alert_date
```

Output fields:

```text
overall
severity
node
issues
signals
```

### `get_nodes_inventory_stats`

Returns aggregate counts over node properties.

Use this for questions like:

```text
How many nodes by status?
What asset_env values exist?
How many nodes per city?
```

Default aggregated fields:

```text
status
asset_env
node_env
loc_city
loc_country
app
os_name
```

You can override them:

```json
{
  "request": {
    "fields": "team_responsible,manufacturer,loc_rack"
  }
}
```

## Generic Filters

`search_nodes` and `count_nodes` support generic filters over node properties:

```json
{
  "request": {
    "filters": {
      "prop": "value"
    }
  }
}
```

Discover valid props with `list_node_props`.

Examples:

```json
{
  "filters": {
    "status": "warn"
  }
}
```

```json
{
  "filters": {
    "asset_env": "prod",
    "loc_city": "Paris, VINCENNES"
  }
}
```

```json
{
  "filters": {
    "manufacturer": "Dell",
    "loc_rack": "A12"
  }
}
```

```json
{
  "filters": {
    "node_env": "TST",
    "status": "down",
    "loc_country": "FR"
  }
}
```

Filters are exact matches. For nodename substring search, use
`nodename_contains` on `search_nodes`.

The generic `filters` object can be combined with shortcut arguments.

These two calls are equivalent:

```json
{
  "request": {
    "filters": {
      "status": "warn",
      "loc_city": "Paris"
    }
  }
}
```

```json
{
  "request": {
    "status": "warn",
    "loc_city": "Paris"
  }
}
```

## Tool Selection

Use `search_nodes` when the user wants rows:

```text
List prod nodes in France.
Show down nodes in Paris.
```

Use `count_nodes` when the user wants one count:

```text
How many prod nodes are in rack A13?
How many nodes are warn in Paris?
```

Use `get_nodes_inventory_stats` when the user wants distributions or possible
values:

```text
How many nodes by status?
What asset_env values exist?
```

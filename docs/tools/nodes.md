# Node Tools

This document describes the OpenSVC Collector MCP tools for node inventory.

Node business logic lives under `src/opensvc_collector_mcp/core/nodes/`, split by concern.
Node Pydantic models live under `src/opensvc_collector_mcp/models/nodes/`.
MCP tool definitions live in `src/opensvc_collector_mcp/tools/nodes.py`.

## Tools

### `list_node_props`

Returns the node properties exposed by the Collector.

Use this before building generic filters for `list_nodes` or `count_nodes`.

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

Returns nodes from the OpenSVC Collector inventory. Use this when the user asks
to list or search nodes matching criteria.

Common arguments:

- `filters`: exact-match filters using node properties.
- `props`: comma-separated node properties to include in the response.
- `orderby`: Collector order expression, for example `nodename` or `~updated`.
- `search`: Collector full-text search expression when supported by `/nodes`.
- `limit`: maximum number of rows to return.
- `offset`: number of matching rows to skip.
- `nodename_contains`: case-insensitive substring search on `nodename`.
- `max_scan`: maximum candidate rows to scan when using `nodename_contains`.

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
      "asset_env": "lab",
      "loc_country": "ZZ",
      "loc_rack": "LAB-RACK-01"
    },
    "props": "nodename,status,asset_env,loc_country,loc_rack",
    "limit": 10,
    "offset": 0,
    "orderby": "nodename"
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
      "loc_city": "Lab City",
      "asset_env": "lab"
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
    "loc_city": "Lab City",
    "asset_env": "lab"
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
    "nodename": "lab-node-01"
  }
}
```

### `get_node_tags`

Returns tags attached to one node selected by exact `nodename`.

Example:

```json
{
  "request": {
    "nodename": "lab-node-01"
  }
}
```

Output fields:

```text
nodename
meta
data
```

### `search_node_by_tag`

Returns nodes attached to one tag selected by exact `tag_name`.

The tool resolves the tag id through `/tags`, then calls:

```text
/tags/<tag_id>/nodes
```

Example:

```json
{
  "request": {
    "tag_name": "test"
  }
}
```

Output fields:

```text
tag_name
tag_id
meta
data
```

### `search_nodes_without_tag`

Returns nodes that do not have one tag attached.

The tool resolves the tag id through `/tags`, lists nodes attached to the tag
through `/tags/<tag_id>/nodes`, then subtracts them from `/nodes?props=nodename`.

Example:

```json
{
  "request": {
    "tag_name": "test"
  }
}
```

Output fields:

```text
tag_name
tag_id
meta
data
```

### `get_node_location`

Returns location fields for one node selected by exact `nodename`.

Example:

```json
{
  "request": {
    "nodename": "lab-node-01"
  }
}
```

Output fields:

```text
nodename
location
raw
```

The `location` object includes datacenter placement fields such as `rack`,
`enclosure`, and `enclosure_slot` when the Collector has them.

### `get_node_organization`

Returns organization fields for one node selected by exact `nodename`.

Example:

```json
{
  "request": {
    "nodename": "lab-node-01"
  }
}
```

Output fields:

```text
nodename
organization
raw
```

The `organization` object includes `responsible`, `integration`, `support`, and
`app`.

### `get_node_hardware`

Returns hardware inventory fields for one node selected by exact `nodename`.

Example:

```json
{
  "request": {
    "nodename": "lab-lyon-01"
  }
}
```

Output fields:

```text
nodename
hardware
cpu
memory
power
placement
raw
```

### `get_node_os`

Returns operating system fields for one node selected by exact `nodename`.

Example:

```json
{
  "request": {
    "nodename": "mcp-full-props-02"
  }
}
```

Output fields:

```text
nodename
os
runtime
raw
```

### `get_node_network`

Returns network addresses for one node selected by exact `nodename`.

The Collector endpoint used is:

```text
/nodes/<nodename>/ips
```

Example:

```json
{
  "request": {
    "nodename": "lab-lyon-01"
  }
}
```

Output fields:

```text
nodename
meta
data
```

### `get_node_compliance`

Returns compliance execution status rows for one node selected by exact
`nodename`.

The Collector endpoint used is:

```text
/nodes/<nodename>/compliance/status
```

Example:

```json
{
  "request": {
    "nodename": "lab-lyon-01"
  }
}
```

Output fields:

```text
nodename
meta
data
```

### `get_node_checks`

Returns live check result rows for one node selected by exact `nodename`.

The Collector endpoint used is:

```text
/nodes/<nodename>/checks
```

Example:

```json
{
  "request": {
    "nodename": "lab-node-01"
  }
}
```

Output fields:

```text
nodename
meta
data
```

### `get_node_disks`

Returns disk inventory rows for one node selected by exact `nodename`.

The Collector endpoint used is:

```text
/nodes/<nodename>/disks
```

Example:

```json
{
  "request": {
    "nodename": "lab-node-01"
  }
}
```

Output fields:

```text
nodename
meta
data
```

### `get_node_cluster`

Returns the cluster associated with one node selected by exact `nodename`.

The tool uses the Collector `/nodes` join props:

```text
nodename,nodes.cluster_id:cluster_id,clusters.cluster_name:cluster_name
```

Example:

```json
{
  "request": {
    "nodename": "mcp-full-props-02"
  }
}
```

Output fields:

```text
nodename
cluster
raw
```

### `get_node_services`

Returns service instances hosted on one node through Collector
`/services_instances`.

The tool filters on `nodes.nodename` and returns joined service and monitor
fields such as `svcname`, `svc_status`, `svc_env`, `svc_app`, `svc_topology`,
`mon_vmname`, and `mon_availstatus`.

Example:

```json
{
  "request": {
    "nodename": "lab-sandbox-01"
  }
}
```

Output fields:

```text
nodename
meta
data
```

Each service row includes `node_names`, the parsed list of nodes from
`svc_nodes`.

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

`list_nodes` and `count_nodes` support generic filters over node properties:

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
    "asset_env": "lab",
    "loc_city": "Lab City"
  }
}
```

```json
{
  "filters": {
    "manufacturer": "LabVendor",
    "loc_rack": "LAB-RACK-01"
  }
}
```

```json
{
  "filters": {
    "node_env": "LAB",
    "status": "down",
    "loc_country": "ZZ"
  }
}
```

Filters are exact matches. For nodename substring search, use
`nodename_contains` on `list_nodes`.

The generic `filters` object can be combined with shortcut arguments.

These two calls are equivalent:

```json
{
  "request": {
    "filters": {
      "status": "warn",
      "loc_city": "Lab City"
    }
  }
}
```

```json
{
  "request": {
    "status": "warn",
    "loc_city": "Lab City"
  }
}
```

## Tool Selection

Use `list_nodes` when the user wants rows:

```text
List lab nodes in Lab Country.
Show down nodes in Lab City.
```

Use `count_nodes` when the user wants one count:

```text
How many lab nodes are in rack LAB-RACK-01?
How many nodes are warn in Lab City?
```

Use `get_nodes_inventory_stats` when the user wants distributions or possible
values:

```text
How many nodes by status?
What asset_env values exist?
```

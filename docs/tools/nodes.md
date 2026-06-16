# Node Tools

This document describes the OpenSVC Collector MCP tools for node inventory.

Node business logic lives under `src/opensvc_collector_mcp/core/nodes/`, split by concern.
Node Pydantic models live under `src/opensvc_collector_mcp/models/nodes/`.
MCP tool definitions live in `src/opensvc_collector_mcp/tools/nodes.py`.

## Tools

### `create_node`

Submits one OpenSVC Collector node through `POST /nodes`. This is a write tool
and requires `write:nodes`, authorized for Collector `NodeManager` or `Manager`
users by MCP RBAC. The MCP `create` tag is descriptive for discovery only.

The Collector API documentation describes `POST /nodes` as both creating a new
node and updating nodes matching the specified query. To keep `create_node` a
strict create tool, MCP first checks `/nodes` with an exact `nodename` filter and
refuses to call `POST /nodes` if a matching node already exists. Collector
remains the final authority for defaults and payload validation. If
`team_responsible` is omitted, Collector defaults it to the user primary group.

Because this changes Collector state, the request requires
`confirmation.phrase`: the assistant must summarize the exact node payload, ask
the user to repeat a concise phrase verbatim, and set `confirmation.phrase` only
after that phrase appears in the latest user message. The confirmation field is
not forwarded to Collector.

Required input fields:

```text
nodename
confirmation.phrase
```

Optional input fields:

```text
properties
```

`properties` is forwarded to Collector with the explicit `nodename` request
field sent as the `nodename` payload property. MCP rejects reserved
`properties.node_id` and `properties.nodename`: Collector generates node ids,
and allowing `node_id` in `POST /nodes` can turn a create request into an
update of an existing node. MCP performs an exact `nodename` existence
pre-check for this create tool; Collector validates the remaining submitted
payload fields.

Example:

```json
{
  "request": {
    "nodename": "lab-node-01",
    "properties": {
      "asset_env": "PPR",
      "loc_city": "Lab City"
    },
    "confirmation": {
      "phrase": "CREATE node lab-node-01 asset_env PPR loc_city Lab City"
    }
  }
}
```

Output fields:

```text
nodename
submitted_properties
collector_response
meta
```

### `delete_node`

Deletes one existing OpenSVC Collector node through `DELETE /nodes/<node_id>`.
Collector cascades this deletion to related service instances, dashboard, checks,
packages, and patches entries. This is a destructive write tool and requires
`delete:nodes`, authorized for Collector `NodeManager` or `Manager` users by MCP
RBAC.

The deletion selector uses the shared `NodeSelector` contract: provide exactly
one of `node_id` or `nodename`. If `nodename` is provided, MCP resolves it with
an exact `/nodes` filter, refuses zero matches, refuses duplicate matches, and
then calls Collector using the resolved `node_id`. Because this is destructive,
the assistant must first resolve or inspect the target, then generate a concise
confirmation phrase containing the exact resolved `node_id` and `nodename`, ask
the user to repeat it verbatim in a new message, and only then call
`delete_node`.

Required input fields:

```text
node_id or nodename
confirm_node_id
confirm_nodename
confirmation.phrase
```

`confirmation.phrase` is the gateway safety gate shared by all state-changing
tools. It must be the exact phrase repeated by the user in the latest message;
the gateway blocks the proxied `call_tool` before MCP execution if the phrase is
missing from that latest message.

Example:

```json
{
  "request": {
    "node_id": "NODE-ID",
    "confirm_node_id": "NODE-ID",
    "confirm_nodename": "lab-node-01",
    "confirmation": {
      "phrase": "DELETE node NODE-ID lab-node-01"
    }
  }
}
```

The tool reads a node snapshot before deleting. The DELETE call is not sent if
`confirm_node_id` differs from the resolved snapshot `node_id`, if
`confirm_nodename` differs from the resolved snapshot nodename, or if the
selector is missing, invalid, or ambiguous. When `node_id` is used as selector,
MCP also verifies the snapshot resolves to that exact `node_id`, which prevents
accidentally passing a nodename in the `node_id` field. The
`confirmation.phrase` field is not forwarded to the Collector; it exists to make
the user confirmation explicit and machine-checkable in the gateway.

Output fields:

```text
node_id
nodename
node
deleted
collector_response
meta
```

### `freeze_node`

Enqueues a freeze action for one OpenSVC Collector node through `PUT /actions`
with `node_id=<node_id>` and `action=freeze`. This is an execution tool and
requires `exec:nodes`, authorized for Collector `NodeExec` or `Manager` users by
MCP RBAC. The action is queued for OpenSVC agents by Collector. MCP annotations
mark it as destructive because it changes operational node behavior.

The request uses the shared `NodeSelector` contract: provide exactly one of
`node_id` or `nodename`. If `nodename` is provided, MCP resolves it with an
exact `/nodes` filter, refuses zero matches, refuses duplicate matches, and then
enqueues the action using the resolved `node_id`. The tool also requires
`confirm_node_id` and `confirm_nodename` to match the resolved snapshot before
calling Collector.

Because this changes runtime state, the request requires `confirmation.phrase`.
The assistant must resolve the selected node, summarize the freeze action, ask
the user to repeat a concise phrase containing the resolved `node_id` and
`nodename` verbatim, and set `confirmation.phrase` only after that phrase appears
in the latest user message.

Required input fields:

```text
node_id or nodename
confirm_node_id
confirm_nodename
confirmation.phrase
```

Example:

```json
{
  "request": {
    "node_id": "NODE-ID",
    "confirm_node_id": "NODE-ID",
    "confirm_nodename": "lab-node-01",
    "confirmation": {
      "phrase": "FREEZE node NODE-ID lab-node-01"
    }
  }
}
```

Output fields:

```text
node_id
nodename
node
action
queued
collector_response
meta
```


### `thaw_node`

Enqueues a thaw/unfreeze action for one OpenSVC Collector node through
`PUT /actions` with `node_id=<node_id>` and `action=thaw`. This is an
execution tool and requires `exec:nodes`, authorized for Collector `NodeExec`
or `Manager` users by MCP RBAC. The action is queued for OpenSVC agents by
Collector. MCP annotations mark it as destructive because it changes
operational node behavior.

The request uses the shared `NodeSelector` contract: provide exactly one of
`node_id` or `nodename`. If `nodename` is provided, MCP resolves it with an
exact `/nodes` filter, refuses zero matches, refuses duplicate matches, and
then enqueues the action using the resolved `node_id`. The tool also requires
`confirm_node_id` and `confirm_nodename` to match the resolved snapshot before
calling Collector.

Because this changes runtime state, the request requires `confirmation.phrase`.
The assistant must resolve the selected node, summarize the thaw action, ask
the user to repeat a concise phrase containing the resolved `node_id` and
`nodename` verbatim, and set `confirmation.phrase` only after that phrase
appears in the latest user message.

Required input fields:

```text
node_id or nodename
confirm_node_id
confirm_nodename
confirmation.phrase
```

Example:

```json
{
  "request": {
    "node_id": "NODE-ID",
    "confirm_node_id": "NODE-ID",
    "confirm_nodename": "lab-node-01",
    "confirmation": {
      "phrase": "THAW node NODE-ID lab-node-01"
    }
  }
}
```

Output fields:

```text
node_id
nodename
node
action
queued
collector_response
meta
```


### `run_node_checks`

Enqueues a checks action for one OpenSVC Collector node through `PUT /actions`
with `node_id=<node_id>` and `action=checks`. This is an execution tool and
requires `exec:nodes`, authorized for Collector `NodeExec` or `Manager` users by
MCP RBAC. The action is queued for OpenSVC agents by Collector. MCP annotations
mark it as non-destructive because it runs checks rather than changing runtime
service or node state, but it is still a state-changing tool because it enqueues
work in Collector.

The request uses the shared `NodeSelector` contract: provide exactly one of
`node_id` or `nodename`. If `nodename` is provided, MCP resolves it with an
exact `/nodes` filter, refuses zero matches, refuses duplicate matches, and then
enqueues the action using the resolved `node_id`. The tool also requires
`confirm_node_id` and `confirm_nodename` to match the resolved snapshot before
calling Collector.

Because this enqueues runtime work, the request requires `confirmation.phrase`.
The assistant must resolve the selected node, summarize the checks action, ask
the user to repeat a concise phrase containing the resolved `node_id` and
`nodename` verbatim, and set `confirmation.phrase` only after that phrase appears
in the latest user message.

Required input fields:

```text
node_id or nodename
confirm_node_id
confirm_nodename
confirmation.phrase
```

Example:

```json
{
  "request": {
    "node_id": "NODE-ID",
    "confirm_node_id": "NODE-ID",
    "confirm_nodename": "lab-node-01",
    "confirmation": {
      "phrase": "RUN checks node NODE-ID lab-node-01"
    }
  }
}
```

Output fields:

```text
node_id
nodename
node
action
queued
collector_response
meta
```


### `collect_node_sysreport`

Enqueues a sysreport collection action for one OpenSVC Collector node through
`PUT /actions` with `node_id=<node_id>` and `action=sysreport`. This is an
execution tool and requires `exec:nodes`, authorized for Collector `NodeExec` or
`Manager` users by MCP RBAC. The action is queued for OpenSVC agents by
Collector. MCP annotations mark it as non-destructive because it collects a
sysreport rather than changing runtime service or node state, but it is still a
state-changing tool because it enqueues work in Collector.

The request uses the shared `NodeSelector` contract: provide exactly one of
`node_id` or `nodename`. If `nodename` is provided, MCP resolves it with an
exact `/nodes` filter, refuses zero matches, refuses duplicate matches, and then
enqueues the action using the resolved `node_id`. The tool also requires
`confirm_node_id` and `confirm_nodename` to match the resolved snapshot before
calling Collector.

Because this enqueues runtime work, the request requires `confirmation.phrase`.
The assistant must resolve the selected node, summarize the sysreport action,
ask the user to repeat a concise phrase containing the resolved `node_id` and
`nodename` verbatim, and set `confirmation.phrase` only after that phrase appears
in the latest user message.

Required input fields:

```text
node_id or nodename
confirm_node_id
confirm_nodename
confirmation.phrase
```

Example:

```json
{
  "request": {
    "node_id": "NODE-ID",
    "confirm_node_id": "NODE-ID",
    "confirm_nodename": "lab-node-01",
    "confirmation": {
      "phrase": "COLLECT sysreport node NODE-ID lab-node-01"
    }
  }
}
```

Output fields:

```text
node_id
nodename
node
action
queued
collector_response
meta
```


### `push_node_asset`

Enqueues a node asset inventory refresh for one OpenSVC Collector node through
`PUT /actions` with `node_id=<node_id>` and `action=pushasset`. This corresponds
to the Collector UI action `Update node information`. It asks the OpenSVC agent
to push node inventory data back to Collector, including fields such as asset
environment, OS, hardware, location, and runtime identity fields. MCP annotations
mark it as non-destructive because it refreshes inventory rather than changing
runtime service or node state, but it is still a state-changing tool because it
enqueues work in Collector.

The request uses the shared `NodeSelector` contract: provide exactly one of
`node_id` or `nodename`. If `nodename` is provided, MCP resolves it with an
exact `/nodes` filter, refuses zero matches, refuses duplicate matches, and then
enqueues the action using the resolved `node_id`. The tool also requires
`confirm_node_id` and `confirm_nodename` to match the resolved snapshot before
calling Collector.

Because this enqueues runtime work, the request requires `confirmation.phrase`.
The assistant must resolve the selected node, summarize the asset inventory
refresh, ask the user to repeat a concise phrase containing the resolved
`node_id` and `nodename` verbatim, and set `confirmation.phrase` only after that
phrase appears in the latest user message.

Required input fields:

```text
node_id or nodename
confirm_node_id
confirm_nodename
confirmation.phrase
```

Example:

```json
{
  "request": {
    "node_id": "NODE-ID",
    "confirm_node_id": "NODE-ID",
    "confirm_nodename": "lab-node-01",
    "confirmation": {
      "phrase": "PUSH asset node NODE-ID lab-node-01"
    }
  }
}
```

Output fields:

```text
node_id
nodename
node
action
queued
collector_response
meta
```


### `snooze_node_notifications`

Snoozes notifications on one OpenSVC Collector node through
`POST /nodes/<node_id>/snooze` with a `duration` field. This is a reversible
state-changing write tool and requires `write:nodes`, authorized for Collector
`NodeManager` or `Manager` users by MCP RBAC. MCP annotations mark it as
non-destructive.

The request uses the shared `NodeSelector` contract: provide exactly one of
`node_id` or `nodename`. If `nodename` is provided, MCP resolves it with an
exact `/nodes` filter, refuses zero matches, refuses duplicate matches, and then
calls Collector using the resolved `node_id`.

Because this changes Collector alerting state, the request requires
`confirmation.phrase`. The assistant must summarize the selected node and
duration, ask the user to repeat a concise phrase verbatim, and set
`confirmation.phrase` only after that phrase appears in the latest user message.

Required input fields:

```text
duration
confirmation.phrase
node_id or nodename
```

Example:

```json
{
  "request": {
    "nodename": "lab-node-01",
    "duration": "1h",
    "confirmation": {
      "phrase": "SNOOZE node lab-node-01 for 1h"
    }
  }
}
```

Output fields:

```text
node_id
nodename
duration
node
snoozed
collector_response
meta
```

### `unsnooze_node_notifications`

Unsnoozes notifications on one OpenSVC Collector node through
`POST /nodes/<node_id>/snooze` without a `duration` field. It is intentionally a
separate tool from `snooze_node_notifications`, so an omitted duration cannot
silently invert the operation. This is a reversible state-changing write tool and
requires `write:nodes`, authorized for Collector `NodeManager` or `Manager` users
by MCP RBAC. MCP annotations mark it as non-destructive.

The request uses the same shared `NodeSelector` contract: provide exactly one of
`node_id` or `nodename`; nodenames are resolved to a single node_id before the
Collector POST is sent. The request also requires `confirmation.phrase`.

Required input fields:

```text
confirmation.phrase
node_id or nodename
```

Example:

```json
{
  "request": {
    "node_id": "NODE-ID",
    "confirmation": {
      "phrase": "UNSNOOZE node NODE-ID"
    }
  }
}
```

Output fields:

```text
node_id
nodename
node
unsnoozed
collector_response
meta
```

### `update_node_properties`

Updates Collector-writable properties on one existing OpenSVC Collector node
through `POST /nodes/<nodename>`. This is a write tool and requires
`write:nodes`, authorized for Collector `NodeManager` or `Manager` users by MCP
RBAC. The MCP `update` tag is descriptive for discovery only. MCP annotations
mark the tool as a destructive write because it updates an existing Collector
node and can overwrite previous property values.

The tool does not expose node creation or deletion. It accepts the fields marked
`writable=true` by the Collector nodes API definition, and rejects fields marked
`writable=false` such as `node_env`. Because it changes Collector state, the
request requires `confirmation.phrase`: the assistant must summarize the exact
node and property changes, ask the user to repeat a concise phrase verbatim, and
set `confirmation.phrase` only after that phrase appears in the latest user
message.

Accepted properties:

```text
action_type
app
asset_env
assetname
cluster_id
collector
connect_to
enclosure
enclosureslot
fqdn
hv
hvpool
hvvdc
hw_obs_alert_date
hw_obs_warn_date
last_comm
listener_port
loc_addr
loc_building
loc_city
loc_country
loc_floor
loc_rack
loc_room
loc_zip
maintenance_end
manufacturer
node_frozen
node_frozen_at
node_id
nodename
notifications
os_obs_alert_date
os_obs_warn_date
power_breaker1
power_breaker2
power_cabinet1
power_cabinet2
power_protect
power_protect_breaker
power_supply_nb
role
sec_zone
snooze_till
status
team_integ
team_responsible
team_support
type
tz
updated
version
warranty_end
```

Example:

```json
{
  "request": {
    "nodename": "lab-node-01",
    "properties": {
      "asset_env": "PPR"
    }
  }
}
```

Example:

```json
{
  "request": {
    "nodename": "lab-node-01",
    "properties": {
      "asset_env": "PPR"
    },
    "confirmation": {
      "phrase": "UPDATE node lab-node-01 asset_env PPR"
    }
  }
}
```

Output fields:

```text
nodename
updated_properties
collector_response
meta
```

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

Use this tool to answer node storage questions. Collector disk sizes such as
`disk_size`, `disk_used`, and `disk_alloc` are expressed in MB. Use `disk_id` to
deduplicate rows before summing totals. `disk_local=true` indicates local node
storage; `disk_local=false` usually indicates SAN/shared storage. Some Collector
responses include nested raw objects (`svcdisks`, `diskinfo`, `stor_array`) in
addition to the flattened fields; prefer the flattened fields when present and
fall back to nested values when needed.

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

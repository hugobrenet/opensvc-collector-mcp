# Node Tools

The node domain exposes typed Collector inventory, write, and runtime-action
tools. Collector remains the final authority for payload validation, endpoint
authorization, and object scope.

This MCP server is not an interaction boundary and is supported only behind the
dedicated harness. The harness owns proposal, user approval, execution
coordination, and audit. MCP request schemas contain business parameters only;
effect tags and annotations provide the harness with operation metadata.

## State-changing tool contract

Existing-node tools accept the stable Collector `node_id` at the MCP boundary.
When a user supplies a nodename, resolve it first with the read-only `get_node`
tool and pass the returned `node_id`. The core layer re-reads the target before
the Collector mutation and rejects missing, ambiguous, or mismatched selectors.
These technical checks protect request integrity; they do not implement user
approval or authorization.

Effect tags remain descriptive:

- `write:nodes` for node inventory or notification writes
- `delete:nodes` for node deletion
- `exec:nodes` for queued node actions

### `create_node`

Creates a node with `POST /nodes`. MCP checks that the exact nodename is absent
because this Collector endpoint otherwise behaves like an upsert. Collector
validates the payload and applies defaults.

Business input:

- `nodename` (required)
- `properties` (optional writable Collector properties)

`node_id` and `nodename` are rejected inside `properties`.

```json
{
  "request": {
    "nodename": "lab-node-01",
    "properties": {
      "asset_env": "PPR",
      "loc_city": "Lab City"
    }
  }
}
```

Tags: `nodes`, `create`, `write:nodes`.
Annotation: `destructiveHint=true`, because Collector creation can otherwise
act as an upsert if the pre-check is bypassed.

### `delete_node`

Deletes one node with `DELETE /nodes/<node_id>`. The public tool accepts only:

```text
node_id
```

The core reads an exact snapshot immediately before deletion and refuses an
unknown, ambiguous, or non-exact id. Collector evaluates whether the
authenticated caller may delete the node.

```json
{
  "request": {
    "node_id": "NODE-ID"
  }
}
```

Tags: `nodes`, `delete`, `delete:nodes`.
Annotation: `destructiveHint=true`.

### Node action tools

Each tool queues exactly one action through `PUT /actions` with the resolved
`node_id`. Every request contains only `node_id`.

| Tool | Collector action | Destructive hint |
|---|---|---:|
| `freeze_node` | `freeze` | true |
| `thaw_node` | `thaw` | false |
| `run_node_checks` | `checks` | false |
| `collect_node_sysreport` | `sysreport` | false |
| `push_node_asset` | `pushasset` | false |
| `push_node_disks` | `pushdisks` | false |
| `push_node_packages` | `pushpkg` | false |
| `push_node_patches` | `pushpatch` | false |
| `push_node_stats` | `pushstats` | false |
| `pull_node_config` | `pull` | false |
| `push_node_config` | `push` | false |
| `update_node_compliance_modules` | `updatecomp` | false |
| `update_node_opensvc_agent` | `updatepkg` | false |
| `scan_node_scsi` | `scanscsi` | false |
| `reboot_node` | `reboot` | true |
| `shutdown_node` | `shutdown` | true |
| `schedule_node_reboot` | `schedule_reboot` | true |
| `unschedule_node_reboot` | `unschedule_reboot` | true |
| `rotate_node_root_password` | `rotate_root_pw` | true |
| `wake_node_on_lan` | `wol` | false |

All action tools carry the `exec:nodes` effect tag. Their annotations describe
risk for harness policy and UX; they are not MCP authorization rules.

```json
{
  "request": {
    "node_id": "NODE-ID"
  }
}
```

### `update_node_properties`

Updates one existing node through `POST /nodes/<resolved nodename>`. The public
request contains:

- `node_id`
- `properties`

MCP resolves the current nodename from `node_id`, validates the writable
property allowlist, and rejects an empty payload. Collector validates values and
authorizes the update.

```json
{
  "request": {
    "node_id": "NODE-ID",
    "properties": {
      "loc_city": "Lab City"
    }
  }
}
```

Tags: `nodes`, `update`, `write:nodes`.
Annotation: `destructiveHint=true`.

### `snooze_node_notifications`

Snoozes notifications with `POST /nodes/<node_id>/snooze`.

Business input:

- `node_id`
- `duration`, using Collector duration syntax such as `30m`, `1h`, or `2d`

```json
{
  "request": {
    "node_id": "NODE-ID",
    "duration": "1h"
  }
}
```

Tags: `nodes`, `snooze`, `write:nodes`.
Annotation: `destructiveHint=false`.

### `unsnooze_node_notifications`

Removes the notification snooze with `POST /nodes/<node_id>/snooze` and no
duration payload.

```json
{
  "request": {
    "node_id": "NODE-ID"
  }
}
```

Tags: `nodes`, `unsnooze`, `write:nodes`.
Annotation: `destructiveHint=false`.

## Read-only tools

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
to list or search nodes matching criteria. The response follows the shared
[pagination contract](../pagination.md).

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

Output fields:

```text
pagination
data
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
pagination
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
pagination
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
pagination
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
pagination
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
pagination
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
pagination
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

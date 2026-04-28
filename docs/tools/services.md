# Service Tools

This document describes the OpenSVC Collector MCP tools for service inventory.

Service business logic lives in `src/opensvc_collector_mcp/core/services_core.py`.
MCP tool definitions live in `src/opensvc_collector_mcp/tools/services.py`.

## Tools

### `list_services`

Returns all OpenSVC Collector services.

By default, this tool returns a compact service inventory view and deliberately
does not include large fields such as `svc_config`.

This tool does not accept filters. For filtered lookup, use `search_services`.

Default props:

```text
svcname,svc_app,svc_env,svc_status,svc_availstatus,svc_topology,svc_nodes,svc_drpnodes,svc_frozen,svc_ha,svc_created,updated
```

Example:

```json
{
  "request": {
    "props": "svcname,svc_app,svc_env,svc_status"
  }
}
```

Output fields:

```text
meta
data
```

### `count_services`

Counts OpenSVC Collector services matching exact-match filters without
returning service rows.

The request supports the same shortcut and generic filters as
`search_services`.

Example:

```json
{
  "request": {
    "svc_env": "LAB",
    "svc_status": "up"
  }
}
```

Output fields:

```text
count
filters
```

### `get_service`

Returns all available OpenSVC Collector information for one service selected by
exact `svcname`.

Use this for service detail inspection. Unlike `list_services`, this endpoint
may include large fields such as `svc_config`.

Example:

```json
{
  "request": {
    "svcname": "tst-lab-service"
  }
}
```

Output fields:

```text
meta
data
```

### `get_service_config`

Returns the OpenSVC service configuration for one service selected by exact
`svcname`.

Use this tool when the question is about the declared service configuration:
global options, section definitions, or raw configuration text. For effective
resource key/value data grouped by resource and node, use `get_service_resources`
instead.

The tool reads Collector `/services/<svcname>` with props limited to
`svcname,svc_config,svc_config_updated,updated`. It returns parsed INI-like
sections by default and also returns the raw config text, bounded by
`raw_config_max_chars`.

Example:

```json
{
  "request": {
    "svcname": "tst-lab-service",
    "include_raw_config": true,
    "include_sections": true,
    "raw_config_max_chars": 20000
  }
}
```

Output fields:

```text
svcname
meta
config_updated
updated
config
sections
```


### `search_frozen_services`

Returns services with currently frozen monitor instances.

Use `filters` for exact service property filters, or the typed shortcut fields
shared with `search_services` such as `svc_env`, `svc_status`, `svc_app`,
`svc_availstatus`, `svc_topology`, and `svc_frozen`. Use `min_frozen_days` to
return only services frozen for at least that many days. In this Collector,
production services use `svc_env=PRD`.

The tool reads Collector `/services_instances`, filters on `svcmon.mon_frozen=1`,
applies the requested service filters as `services.<prop>=<value>`, and groups
matching frozen instances by `svcname`.

Example:

```json
{
  "request": {
    "filters": {
      "svc_env": "LAB",
      "svc_status": "up"
    },
    "min_frozen_days": 15
  }
}
```

Output fields:

```text
meta
services
```

### `search_services_by_tag`

Returns services that have one exact OpenSVC Collector tag attached.

The tool resolves the tag through Collector `/tags`, then calls
`/tags/<tag_id>/services` using internal paged retrieval. Returned services are
deduplicated by `svcname` because Collector can expose several rows for the same
service/tag relation.

Use `meta.service_count` to count unique tagged services. `meta.raw_count` is the
raw Collector row count and `meta.duplicate_count` is the number of removed
duplicate rows.

Example:

```json
{
  "request": {
    "tag_name": "LAB-TAG",
    "props": "svcname,svc_app,svc_env,svc_status"
  }
}
```

Output fields:

```text
tag_name
tag_id
tag
meta
data
```

### `search_services_without_tag`

Returns services that do not have one exact OpenSVC Collector tag attached.

The tool resolves the tag through Collector `/tags`, lists services attached to
that tag through `/tags/<tag_id>/services`, lists all services through
`/services`, then returns the difference by `svcname`.

Use `meta.service_count` to count services without the tag, `meta.tagged_count`
to count unique services with the tag, `meta.tagged_raw_count` to inspect the raw
Collector row count for tagged services, and `meta.total_services` to see the
full service population scanned.

Example:

```json
{
  "request": {
    "tag_name": "LAB-TAG",
    "props": "svcname,svc_app,svc_env,svc_status"
  }
}
```

Output fields:

```text
tag_name
tag_id
tag
meta
data
```


### `get_service_tags`

Returns OpenSVC Collector tags attached to one service selected by exact
`svcname`.

Use this tool when the question is about service classification, ownership,
policy markers, or other metadata represented as Collector tags. The tool reads
Collector `/services/<svcname>/tags` using internal paged retrieval, so it is
not limited to the first Collector page.

Use exact filters such as `tag_name`, `tag_id`, or `tag_exclude` to narrow the
result. Default output uses compact tag properties.

Example:

```json
{
  "request": {
    "svcname": "tst-lab-service",
    "tag_name": "LAB-TAG"
  }
}
```

Output fields:

```text
svcname
meta
data
```


### `get_service_checks`

Returns live OpenSVC Collector checks for one service selected by exact
`svcname`.

Use this tool to inspect check values, thresholds, and error flags for a service.
The tool reads Collector `/services/<svcname>/checks` using internal paged
retrieval, so it is not limited to the first Collector page. Use exact filters
such as `chk_type`, `chk_err`, `chk_instance`, or `node_id` to narrow the result.

Default output uses compact check properties and excludes no large payload field.
`max_checks` is a safety guardrail for unusually large services.

Example:

```json
{
  "request": {
    "svcname": "tst-lab-service",
    "chk_err": 1,
    "max_checks": 10000
  }
}
```

Output fields:

```text
svcname
meta
data
```


### `get_service_alerts`

Returns current OpenSVC Collector dashboard alerts for one service selected by
exact `svcname`.

Use this tool to inspect active service alerts. For historical action execution
logs use `get_service_actions`; for unacknowledged action errors use
`get_service_unacknowledged_errors`; for interpreted status use
`get_service_health`.

The tool reads Collector `/services/<svcname>/alerts` with compact alert
properties by default. Use exact filters such as `dash_type`, `dash_severity`,
or `node_id` to narrow the result. Pagination is explicit with `limit` and
`offset`.

Example:

```json
{
  "request": {
    "svcname": "tst-lab-service",
    "dash_type": "action errors",
    "limit": 10,
    "offset": 0
  }
}
```

Output fields:

```text
svcname
meta
data
```


### `get_service_actions`

Returns recent or paginated OpenSVC action history for one service selected by
exact `svcname`.

Use this tool to inspect actions executed on a service, such as starts, stops,
provisions, syncs, freezes, and related errors. By default, `latest` is true, so
it returns the newest matching actions without requiring the client to calculate
an offset from Collector `meta.total`.

Use exact filters such as `action`, `status`, `ack`, `rid`, and `subset` to
focus the history. Full `status_log` values can be large, so they are excluded
by default. The tool returns a truncated `status_log_preview` by default when a
log is available.

Example:

```json
{
  "request": {
    "svcname": "tst-lab-service",
    "status": "err",
    "limit": 10,
    "latest": true
  }
}
```

Output fields:

```text
svcname
meta
data
```

### `get_service_unacknowledged_errors`

Returns recent or paginated OpenSVC action errors that are still unacknowledged
for one service selected by exact `svcname`.

Use this tool to focus directly on service action failures that still require
attention. The Collector endpoint is already scoped to error and unacknowledged
action rows, so the request intentionally does not expose `status` or `ack` as
parameters. Use `action`, `rid`, `subset`, or generic action filters such as
`hostid` and `node_id` only to narrow the result.

By default, `latest` is true and full `status_log` values are excluded. The tool
returns `status_log_preview` when a log is available, keeping responses usable
for LLM clients while preserving enough error context.

Example:

```json
{
  "request": {
    "svcname": "tst-lab-service",
    "action": "start",
    "limit": 10,
    "latest": true
  }
}
```

Output fields:

```text
svcname
meta
data
```


### `get_service_health`

Returns an interpreted health summary for one service selected by exact
`svcname`.

The tool combines service-level status fields and node-level instance monitor
state. It reports an overall state, worst severity, concrete issues, and the raw
signals used for interpretation.

Example:

```json
{
  "request": {
    "svcname": "tst-lab-service"
  }
}
```

Output fields:

```text
overall
severity
service
issues
signals
```

### `list_service_props`

Returns available OpenSVC Collector service properties.

Use this before service list or search tools to choose valid field names.
For service tools, prefer `service_props` values in `props` and exact-match
filters. `available_props` preserves the raw Collector property names for
inspection.

Example:

```json
{}
```

Output fields:

```text
count
available_props
service_props
```

### `get_service_instances`

Returns node-level OpenSVC Collector instances for one service selected by exact
`svcname`.

Use this after `search_services` or `get_service` to answer where a service is
running and what its monitor state is on each node.

The tool filters Collector `/services_instances` on `services.svcname` and
returns joined service, node, and monitor fields.

Example:

```json
{
  "request": {
    "svcname": "tst-lab-service"
  }
}
```

Output fields:

```text
svcname
meta
data
```

### `get_service_nodes`

Returns Collector node monitor rows for one service selected by exact `svcname`.

Use this tool to identify the nodes where Collector knows the service and inspect
per-node monitor state such as overall status, availability status, frozen state,
last update time, and monitor VM name. This is different from
`get_service_instances`, which reads the global `/services_instances` collection;
`get_service_nodes` is scoped directly through `/services/<svcname>/nodes`.

Example:

```json
{
  "request": {
    "svcname": "tst-lab-service"
  }
}
```

Output fields:

```text
svcname
meta
data
```

Each `data` row commonly includes:

```text
nodename
node_id
mon_vmname
mon_overallstatus
mon_availstatus
mon_frozen
mon_frozen_at
mon_encap_frozen_at
mon_updated
mon_changed
```


### `get_service_hbas`

Returns HBA rows attached to one service selected by exact `svcname`.

Use this tool to list service storage adapters by node. The returned `hba_id` can
be used to filter service targets through `get_service_targets`. Typical HBA
types include Fibre Channel (`fc`) and iSCSI (`iscsi`).

Example:

```json
{
  "request": {
    "svcname": "tst-lab-service"
  }
}
```

Output fields:

```text
svcname
meta
data
```

Each `data` row commonly includes:

```text
nodename
node_id
hba_id
hba_type
updated
```


### `get_service_targets`

Returns storage target rows attached to one service selected by exact `svcname`.

Use this tool to inspect the storage targets reachable by service HBAs. It can be
filtered by `hba_id`, `node_id`, `tgt_id`, or `array_name`, which makes it the
natural follow-up to `get_service_hbas` when the user wants to understand SAN
paths behind a specific HBA.

Example:

```json
{
  "request": {
    "svcname": "tst-lab-service",
    "hba_id": "LAB-HBA-01"
  }
}
```

Output fields:

```text
svcname
meta
data
```

Each `data` row commonly includes:

```text
nodename
node_id
hba_id
tgt_id
array_name
array_model
array_firmware
array_comment
updated
```


### `get_service_disks`

Returns disk rows attached to one service selected by exact `svcname`.

Use this tool to list service disks with their node, size, local/SAN state, disk
identity, storage group, and array information. This is more direct than
`get_service_resources` when the user asks which disks are attached to a service.

Example:

```json
{
  "request": {
    "svcname": "tst-lab-service"
  }
}
```

Output fields:

```text
svcname
meta
data
```

Each `data` row commonly includes:

```text
nodename
node_id
disk_id
disk_name
disk_size
disk_used
disk_local
disk_vendor
disk_model
disk_devid
disk_alloc
disk_raid
disk_group
disk_arrayid
array_name
array_model
disk_updated
```


### `get_service_resources`

Returns grouped OpenSVC resource information for one service selected by exact
`svcname`.

The tool reads Collector `/services/<svcname>/resinfo`, which exposes resource
information as key/value rows, then groups those rows by resource id and node.
This avoids parsing `svc_config` while keeping the resource payload useful for
LLMs.

Example:

```json
{
  "request": {
    "svcname": "tst-lab-service"
  }
}
```

Output fields:

```text
svcname
meta
resources
```

### `search_services`

Searches OpenSVC Collector services with exact-match filters and explicit
pagination. It does not perform substring, wildcard, or fuzzy search.

Shortcut filters:

```text
svcname
svc_app
svc_env
svc_status
svc_availstatus
svc_topology
svc_frozen
```

Generic filters can be passed with service properties discovered through
`list_service_props`.

Example:

```json
{
  "request": {
    "svc_env": "LAB",
    "svc_status": "up",
    "limit": 20,
    "offset": 0
  }
}
```

Generic filter example:

```json
{
  "request": {
    "filters": {
      "svc_app": "LAB-APP",
      "svc_topology": "failover"
    },
    "props": "svcname,svc_app,svc_env,svc_status"
  }
}
```

Output fields:

```text
meta
data
```

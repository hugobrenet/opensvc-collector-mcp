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

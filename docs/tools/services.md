# Service Tools

This document describes the OpenSVC Collector MCP tools for service inventory.

Service business logic lives in `src/opensvc_collector_mcp/core/services_core.py`.
MCP tool definitions live in `src/opensvc_collector_mcp/tools/services.py`.

## Pagination Strategy

`list_services` uses `prefer_pagination`: it calls `/services` through the
shared `collector_get_all(..., strategy="paged")` helper and walks
`limit/offset` pages internally.

`search_services` uses user-facing pagination. It sends one Collector GET to
`/services` with exact-match filters plus explicit `limit` and `offset`, and
uses Collector `meta.total` instead of fetching all matches.

`count_services` does not paginate. It sends one Collector GET to `/services`
with `props=svcname`, `limit=1`, `offset=0`, and exact-match filters, then
returns Collector `meta.total`.

`get_service` does not paginate. It reads the single object endpoint
`/services/<svcname>` and returns the Collector response for that service.

`get_service_health` does not expose pagination. It calls the single service
detail endpoint and the paged `/services_instances` lookup, then returns an
interpreted health summary.

`get_service_instances` uses `prefer_pagination`: it calls
`/services_instances` through the shared `collector_get_all(...,
strategy="paged")` helper and filters on `services.svcname`.

`get_service_resources` uses `prefer_pagination`: it calls
`/services/<svcname>/resinfo` through the shared `collector_get_all(...,
strategy="paged")` helper, then groups Collector key/value rows by resource id
and node.

`list_service_props` does not paginate. It performs one Collector GET on
`/services` with `props=svcname` and reads `meta.available_props`; the returned
service row is not used as inventory data.

Future service collection tools should choose an explicit strategy:

- Use `prefer_pagination` for broad `/services` and `/services_instances`
  collection scans.
- Use `safe_limit_zero` only for bounded, service-scoped subresources after
  validating the Collector cardinality with real data.
- Keep user-facing search tools paginated with explicit `limit` and `offset`.

## Tool Selection

Use `list_service_props` when the client needs to discover valid service
properties before building a `props` list or exact-match filters.

Use `list_services` when the client needs a broad service inventory scan. This
tool is not filtered; use `search_services` for targeted lookup.

Use `search_services` when the client needs service rows matching one or more
exact service property values. This tool does not do substring or fuzzy search.

Use `count_services` when the client only needs the number of services matching
exact filters and does not need service rows.

Use `get_service` when the client already knows the exact `svcname` and needs
the full detail payload for that single service. If the exact `svcname` is not
known, use `search_services` first.

Use `get_service_health` when the client needs an interpreted service health
summary instead of raw service and instance rows.

Use `get_service_instances` when the client already knows the exact `svcname`
and needs the node-level instances for that service, including monitor state per
node.

Use `get_service_resources` when the client already knows the exact `svcname`
and needs resource-level information such as disks, filesystems, IPs,
containers, app resources, sync resources, and their key/value properties.

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

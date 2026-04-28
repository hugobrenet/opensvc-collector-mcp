# Service Tools

This document describes the OpenSVC Collector MCP tools for service inventory.

Service business logic lives in `src/opensvc_collector_mcp/core/services_core.py`.
MCP tool definitions live in `src/opensvc_collector_mcp/tools/services.py`.

## Pagination Strategy

`list_service_props` does not paginate. It performs one Collector GET on
`/services` with `props=svcname` and reads `meta.available_props`; the returned
service row is not used as inventory data.

Future service collection tools should choose an explicit strategy:

- Use `prefer_pagination` for broad `/services` and `/services_instances`
  collection scans.
- Use `safe_limit_zero` only for bounded, service-scoped subresources after
  validating the Collector cardinality with real data.
- Keep user-facing search tools paginated with explicit `limit` and `offset`.

## Tools

### `list_service_props`

Returns available OpenSVC Collector service properties.

Use this before service list or search tools to choose valid `props` and
exact-match filters.

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

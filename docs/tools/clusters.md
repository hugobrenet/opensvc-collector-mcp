# Cluster Tools

This document describes the OpenSVC Collector MCP tools for cluster inventory.

Cluster business logic lives under `src/opensvc_collector_mcp/core/clusters/`.
Cluster Pydantic models live under `src/opensvc_collector_mcp/models/clusters/`.
MCP tool definitions live in `src/opensvc_collector_mcp/tools/clusters.py`.

## Tools

### `get_cluster_nodes`

Returns one page of nodes belonging to a cluster selected by exact `cluster_name`.

The request supports the standard Collector collection arguments: `limit`,
`offset`, `orderby`, `filters`, `search`, and `props`.

The tool uses the Collector `/nodes` join props:

```text
nodename,clusters.cluster_name:cluster_name
```

and filters with:

```text
clusters.cluster_name=<cluster_name>
```

Example:

```json
{
  "request": {
    "cluster_name": "mcp-cluster-a",
    "limit": 20,
    "offset": 0,
    "orderby": "nodename"
  }
}
```

Output fields:

```text
cluster_name
meta
data
```

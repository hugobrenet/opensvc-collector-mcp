# Cluster Tools

This document describes the OpenSVC Collector MCP tools for cluster inventory.

Cluster business logic lives under `src/opensvc_collector_mcp/core/clusters/`.
Cluster Pydantic models live under `src/opensvc_collector_mcp/models/clusters/`.
MCP tool definitions live in `src/opensvc_collector_mcp/tools/clusters.py`.

## Tools

### `get_cluster_nodes`

Returns nodes belonging to one cluster selected by exact `cluster_name`.

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
    "cluster_name": "mcp-cluster-a"
  }
}
```

Output fields:

```text
cluster_name
meta
data
```

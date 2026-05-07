# Disk Tools

This document describes the OpenSVC Collector MCP tools for global disk inventory.

Disk business logic lives under `src/opensvc_collector_mcp/core/disks/`.
Disk Pydantic models live under `src/opensvc_collector_mcp/models/disks/`.
MCP tool definitions live in `src/opensvc_collector_mcp/tools/disks.py`.

## Tools

### `list_disk_props`

Returns the disk properties exposed by the Collector `/disks` endpoint.

Use this before building generic filters for `list_disks`, or before selecting
custom `props` for disk rows. Raw Collector property names include table
prefixes such as `svcdisks.`, `diskinfo.`, and `stor_array.`.

Output fields:

```text
count
available_props
disk_props
```

### `count_disks`

Counts OpenSVC Collector disk rows matching exact-match filters without
returning disk rows. This uses `/disks` collection metadata with `limit=1`.

Example:

```json
{
  "request": {
    "filters": {
      "node_id": "NODE-ID"
    }
  }
}
```

Output fields:

```text
count
filters
search
```

### `list_disks`

Lists OpenSVC Collector disk rows through `/disks` with optional exact-match
filters, Collector search, ordering, pagination, and selectable `props`.

The default response uses table-prefixed props and aliases to return a flat disk
view with service attachment fields, diskinfo fields, and storage array fields.
If custom `props` are provided, use raw Collector prop names from
`list_disk_props`. For global inventory, `disk_id` is the stable identifier to
use for deduplication and for `get_disk`.

Example:

```json
{
  "request": {
    "filters": {
      "node_id": "NODE-ID"
    },
    "limit": 20,
    "offset": 0
  }
}
```

Common request filters:

```text
node_id       -> svcdisks.node_id
svc_id        -> svcdisks.svc_id
app_id        -> svcdisks.app_id
disk_id       -> diskinfo.disk_id
disk_local    -> svcdisks.disk_local
disk_group    -> diskinfo.disk_group
disk_arrayid  -> diskinfo.disk_arrayid
array_name    -> stor_array.array_name
```

The tool also accepts raw Collector property names in `filters`.

Common output fields:

```text
id
node_id
svc_id
app_id
disk_id
disk_size      # MB
disk_used      # MB
disk_local
disk_dg
disk_vendor
disk_model
disk_name
disk_devid
disk_alloc     # MB when returned
disk_raid
disk_group
disk_arrayid
array_id
array_name
array_model
```

### `get_disk`

Returns one OpenSVC Collector disk through `/disks/<id>`.

Important: the tool expects the stable `disk_id` value. It first calls
`/disks/<id>`. If Collector returns 404 for a valid local disk id, it falls back
to `/disks` filtered on `diskinfo.disk_id`. It does not use the numeric
`svcdisks.id` or `diskinfo.id` row ids.

Example:

```json
{
  "request": {
    "disk": "DISK-ID"
  }
}
```

Output fields:

```text
disk
meta
data
```

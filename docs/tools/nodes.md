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

`delete_node` is intentionally `node_id` only at execution time. It does not
accept `nodename` as an execution selector. If the user provides only a nodename,
the assistant must first call a read-only resolver such as `get_node`, ensure it
resolves to exactly one Collector node, and read both the resolved `node_id` and
`nodename`. Only after that resolution step should the assistant ask for the
confirmation phrase.

Because this is destructive, the confirmation phrase must contain both resolved
values, for example `DELETE node <node_id> <nodename>`. When the latest user
message contains that exact phrase, call `delete_node` with the resolved
`node_id`, matching `confirm_node_id`, matching `confirm_nodename`, and
`confirmation.phrase`. Never pass a nodename value as `node_id`, and never add a
`nodename` field to the `delete_node` request.

Required input fields:

```text
node_id
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
`confirm_node_id` differs from `node_id`, if `confirm_node_id` differs from the
resolved snapshot `node_id`, if `confirm_nodename` differs from the resolved
snapshot nodename, or if `node_id` is missing or invalid. MCP verifies the
snapshot resolves to the exact `node_id`, which prevents accidentally passing a
nodename in the `node_id` field. The `confirmation.phrase` field is not
forwarded to the Collector; it exists to make the user confirmation explicit and
machine-checkable in the gateway.

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

The request is `node_id` only. If the user provides a `nodename`, first call
`get_node` to resolve exactly one node and read its `node_id` and `nodename`.
Do not ask for confirmation before this resolution step. The tool also requires
`confirm_node_id` and `confirm_nodename` to match the resolved snapshot before
calling Collector. Do not pass `nodename` as an execution selector.

Because this changes runtime state, the request requires `confirmation.phrase`.
The assistant must resolve the selected node, summarize the freeze action, ask
the user to repeat a concise phrase containing the resolved `node_id` and
`nodename` verbatim, and set `confirmation.phrase` only after that phrase appears
in the latest user message.

Required input fields:

```text
node_id
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

The request is `node_id` only. If the user provides a `nodename`, first call
`get_node` to resolve exactly one node and read its `node_id` and `nodename`.
Do not ask for confirmation before this resolution step. The tool also requires
`confirm_node_id` and `confirm_nodename` to match the resolved snapshot before
calling Collector. Do not pass `nodename` as an execution selector.

Because this changes runtime state, the request requires `confirmation.phrase`.
The assistant must resolve the selected node, summarize the thaw action, ask
the user to repeat a concise phrase containing the resolved `node_id` and
`nodename` verbatim, and set `confirmation.phrase` only after that phrase
appears in the latest user message.

Required input fields:

```text
node_id
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

The request is `node_id` only. If the user provides a `nodename`, first call
`get_node` to resolve exactly one node and read its `node_id` and `nodename`.
Do not ask for confirmation before this resolution step. The tool also requires
`confirm_node_id` and `confirm_nodename` to match the resolved snapshot before
calling Collector. Do not pass `nodename` as an execution selector.

Because this enqueues runtime work, the request requires `confirmation.phrase`.
The assistant must resolve the selected node, summarize the checks action, ask
the user to repeat a concise phrase containing the resolved `node_id` and
`nodename` verbatim, and set `confirmation.phrase` only after that phrase appears
in the latest user message.

Required input fields:

```text
node_id
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

The request is `node_id` only. If the user provides a `nodename`, first call
`get_node` to resolve exactly one node and read its `node_id` and `nodename`.
Do not ask for confirmation before this resolution step. The tool also requires
`confirm_node_id` and `confirm_nodename` to match the resolved snapshot before
calling Collector. Do not pass `nodename` as an execution selector.

Because this enqueues runtime work, the request requires `confirmation.phrase`.
The assistant must resolve the selected node, summarize the sysreport action,
ask the user to repeat a concise phrase containing the resolved `node_id` and
`nodename` verbatim, and set `confirmation.phrase` only after that phrase appears
in the latest user message.

Required input fields:

```text
node_id
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

The request is `node_id` only. If the user provides a `nodename`, first call
`get_node` to resolve exactly one node and read its `node_id` and `nodename`.
Do not ask for confirmation before this resolution step. The tool also requires
`confirm_node_id` and `confirm_nodename` to match the resolved snapshot before
calling Collector. Do not pass `nodename` as an execution selector.

Because this enqueues runtime work, the request requires `confirmation.phrase`.
The assistant must resolve the selected node, summarize the asset inventory
refresh, ask the user to repeat a concise phrase containing the resolved
`node_id` and `nodename` verbatim, and set `confirmation.phrase` only after that
phrase appears in the latest user message.

Required input fields:

```text
node_id
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


### `push_node_disks`

Enqueues a node disk inventory refresh for one OpenSVC Collector node through
`PUT /actions` with `node_id=<node_id>` and `action=pushdisks`. This corresponds
to the Collector UI action `Update disks information`. It asks the OpenSVC agent
to push disk/storage inventory data back to Collector. MCP annotations mark it
as non-destructive because it refreshes inventory rather than changing runtime
service or node state, but it is still a state-changing tool because it enqueues
work in Collector.

The request is `node_id` only. If the user provides a `nodename`, first call
`get_node` to resolve exactly one node and read its `node_id` and `nodename`.
Do not ask for confirmation before this resolution step. The tool also requires
`confirm_node_id` and `confirm_nodename` to match the resolved snapshot before
calling Collector. Do not pass `nodename` as an execution selector.

Because this enqueues runtime work, the request requires `confirmation.phrase`.
The assistant must resolve the selected node, summarize the disk inventory
refresh, ask the user to repeat a concise phrase containing the resolved
`node_id` and `nodename` verbatim, and set `confirmation.phrase` only after that
phrase appears in the latest user message.

Required input fields:

```text
node_id
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
      "phrase": "PUSH disks node NODE-ID lab-node-01"
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


### `push_node_packages`

Enqueues a node installed package inventory refresh for one OpenSVC Collector
node through `PUT /actions` with `node_id=<node_id>` and `action=pushpkg`. This
corresponds to the Collector UI action `Update installed packages information`.
It asks the OpenSVC agent to push package inventory data back to Collector. MCP
annotations mark it as non-destructive because it refreshes inventory rather
than changing runtime service or node state, but it is still a state-changing
tool because it enqueues work in Collector.

The request is `node_id` only. If the user provides a `nodename`, first call
`get_node` to resolve exactly one node and read its `node_id` and `nodename`.
Do not ask for confirmation before this resolution step. The tool also requires
`confirm_node_id` and `confirm_nodename` to match the resolved snapshot before
calling Collector. Do not pass `nodename` as an execution selector.

Because this enqueues runtime work, the request requires `confirmation.phrase`.
The assistant must resolve the selected node, summarize the package inventory
refresh, ask the user to repeat a concise phrase containing the resolved
`node_id` and `nodename` verbatim, and set `confirmation.phrase` only after that
phrase appears in the latest user message.

Required input fields:

```text
node_id
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
      "phrase": "PUSH packages node NODE-ID lab-node-01"
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


### `push_node_patches`

Enqueues a node installed patch inventory refresh for one OpenSVC Collector node
through `PUT /actions` with `node_id=<node_id>` and `action=pushpatch`. This
corresponds to the Collector UI action `Update installed patches information`.
It asks the OpenSVC agent to push patch inventory data back to Collector. MCP
annotations mark it as non-destructive because it refreshes inventory rather
than changing runtime service or node state, but it is still a state-changing
tool because it enqueues work in Collector.

The request is `node_id` only. If the user provides a `nodename`, first call
`get_node` to resolve exactly one node and read its `node_id` and `nodename`.
Do not ask for confirmation before this resolution step. The tool also requires
`confirm_node_id` and `confirm_nodename` to match the resolved snapshot before
calling Collector. Do not pass `nodename` as an execution selector.

Because this enqueues runtime work, the request requires `confirmation.phrase`.
The assistant must resolve the selected node, summarize the patch inventory
refresh, ask the user to repeat a concise phrase containing the resolved
`node_id` and `nodename` verbatim, and set `confirmation.phrase` only after that
phrase appears in the latest user message.

Required input fields:

```text
node_id
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
      "phrase": "PUSH patches node NODE-ID lab-node-01"
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


### `push_node_stats`

Enqueues a node statistics refresh for one OpenSVC Collector node through
`PUT /actions` with `node_id=<node_id>` and `action=pushstats`. This corresponds
to the Collector UI action `Update stats`. It asks the OpenSVC agent to push node
statistics back to Collector. MCP annotations mark it as non-destructive because
it refreshes statistics rather than changing runtime service or node state, but
it is still a state-changing tool because it enqueues work in Collector.

The request is `node_id` only. If the user provides a `nodename`, first call
`get_node` to resolve exactly one node and read its `node_id` and `nodename`.
Do not ask for confirmation before this resolution step. The tool also requires
`confirm_node_id` and `confirm_nodename` to match the resolved snapshot before
calling Collector. Do not pass `nodename` as an execution selector.

Because this enqueues runtime work, the request requires `confirmation.phrase`.
The assistant must resolve the selected node, summarize the statistics refresh,
ask the user to repeat a concise phrase containing the resolved `node_id` and
`nodename` verbatim, and set `confirmation.phrase` only after that phrase appears
in the latest user message.

Required input fields:

```text
node_id
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
      "phrase": "PUSH stats node NODE-ID lab-node-01"
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


### `pull_node_config`

Enqueues a node-only OpenSVC configuration pull for one Collector node through
`PUT /actions` with `node_id=<node_id>` and `action=pull`. Collector formats
this as a node action equivalent to `nodemgr pull` for the resolved node. This is
not a service-instance Pull tool and does not take `svc_id`. MCP annotations mark
it as non-destructive, but it is still a state-changing tool because it enqueues
work in Collector and can synchronize node configuration.

The request is `node_id` only. If the user provides a `nodename`, first call
`get_node` to resolve exactly one node and read its `node_id` and `nodename`.
Do not ask for confirmation before this resolution step. The tool also requires
`confirm_node_id` and `confirm_nodename` to match the resolved snapshot before
calling Collector. Do not pass `nodename` as an execution selector.

Because this enqueues runtime work, the request requires `confirmation.phrase`.
The assistant must resolve the selected node, summarize the node configuration
pull, ask the user to repeat a concise phrase containing the resolved `node_id`
and `nodename` verbatim, and set `confirmation.phrase` only after that phrase
appears in the latest user message.

Required input fields:

```text
node_id
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
      "phrase": "PULL config node NODE-ID lab-node-01"
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


### `push_node_config`

Enqueues a node-only OpenSVC configuration push for one Collector node through
`PUT /actions` with `node_id=<node_id>` and `action=push`. Collector formats
this as a node action equivalent to `nodemgr push` for the resolved node. This is
not a service-instance Push tool and does not take `svc_id`. MCP annotations mark
it as non-destructive, but it is still a state-changing tool because it enqueues
work in Collector and can synchronize node configuration.

The request is `node_id` only. If the user provides a `nodename`, first call
`get_node` to resolve exactly one node and read its `node_id` and `nodename`.
Do not ask for confirmation before this resolution step. The tool also requires
`confirm_node_id` and `confirm_nodename` to match the resolved snapshot before
calling Collector. Do not pass `nodename` as an execution selector.

Because this enqueues runtime work, the request requires `confirmation.phrase`.
The assistant must resolve the selected node, summarize the node configuration
push, ask the user to repeat a concise phrase containing the resolved `node_id`
and `nodename` verbatim, and set `confirmation.phrase` only after that phrase
appears in the latest user message.

Required input fields:

```text
node_id
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
      "phrase": "PUSH config node NODE-ID lab-node-01"
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


### `update_node_compliance_modules`

Enqueues a compliance modules update for one OpenSVC Collector node through
`PUT /actions` with `node_id=<node_id>` and `action=updatecomp`. This
corresponds to the Collector UI action `Update compliance modules`. It asks the
OpenSVC agent to download and install compliance module tarballs from
`node.repocomp` or `node.repo/compliance`. MCP annotations mark it as
non-destructive, but it is still a state-changing tool because it enqueues work
in Collector and updates files on the node.

The request is `node_id` only. If the user provides a `nodename`, first call
`get_node` to resolve exactly one node and read its `node_id` and `nodename`.
Do not ask for confirmation before this resolution step. The tool also requires
`confirm_node_id` and `confirm_nodename` to match the resolved snapshot before
calling Collector. Do not pass `nodename` as an execution selector.

Because this enqueues runtime work, the request requires `confirmation.phrase`.
The assistant must resolve the selected node, summarize the compliance modules
update, ask the user to repeat a concise phrase containing the resolved
`node_id` and `nodename` verbatim, and set `confirmation.phrase` only after that
phrase appears in the latest user message.

Required input fields:

```text
node_id
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
      "phrase": "UPDATE compliance modules node NODE-ID lab-node-01"
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


### `update_node_opensvc_agent`

Enqueues an OpenSVC agent package update for one Collector node through
`PUT /actions` with `node_id=<node_id>` and `action=updatepkg`. This corresponds
to the Collector UI action `Update opensvc agent`. It upgrades only the OpenSVC
agent package from `node.repopkg` or `node.repo/packages` using the node OS
package backend; it is not a general OS package update. MCP annotations mark it
as non-destructive, but it is still a state-changing tool because it enqueues
work in Collector and updates the OpenSVC agent package on the node.

The request is `node_id` only. If the user provides a `nodename`, first call
`get_node` to resolve exactly one node and read its `node_id` and `nodename`.
Do not ask for confirmation before this resolution step. The tool also requires
`confirm_node_id` and `confirm_nodename` to match the resolved snapshot before
calling Collector. Do not pass `nodename` as an execution selector.

Because this enqueues runtime work, the request requires `confirmation.phrase`.
The assistant must resolve the selected node, summarize the OpenSVC agent
package update, ask the user to repeat a concise phrase containing the resolved
`node_id` and `nodename` verbatim, and set `confirmation.phrase` only after that
phrase appears in the latest user message.

Required input fields:

```text
node_id
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
      "phrase": "UPDATE opensvc agent node NODE-ID lab-node-01"
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


### `scan_node_scsi`

Enqueues a SCSI host rescan for one OpenSVC Collector node through
`PUT /actions` with `node_id=<node_id>` and `action=scanscsi`. This corresponds
to the Collector UI action `Rescan scsi hosts`. It asks the OpenSVC agent to
rescan the node operating system SCSI host buses for newly presented LUNs or
disks. It is not a simple Collector disk inventory refresh; use
`push_node_disks` later if the user wants Collector disk inventory refreshed
after discovery. MCP annotations mark it as non-destructive, but it is still a
state-changing tool because it enqueues work in Collector and triggers an OS
storage bus scan on the node.

The request is `node_id` only. If the user provides a `nodename`, first call
`get_node` to resolve exactly one node and read its `node_id` and `nodename`.
Do not ask for confirmation before this resolution step. The tool also requires
`confirm_node_id` and `confirm_nodename` to match the resolved snapshot before
calling Collector. Do not pass `nodename` as an execution selector.

Because this enqueues runtime work, the request requires `confirmation.phrase`.
The assistant must resolve the selected node, summarize the SCSI host rescan,
ask the user to repeat a concise phrase containing the resolved `node_id` and
`nodename` verbatim, and set `confirmation.phrase` only after that phrase appears
in the latest user message.

Required input fields:

```text
node_id
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
      "phrase": "SCAN scsi node NODE-ID lab-node-01"
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


### `reboot_node`

Enqueues an immediate reboot action for one OpenSVC Collector node through
`PUT /actions` with `node_id=<node_id>` and `action=reboot`. This corresponds
to the Collector UI action `Reboot`. It asks the OpenSVC agent to reboot the
target node as soon as the queued action is executed. Unlike
`schedule_node_reboot`, this tool does not set a future reboot flag and does not
wait for a configured reboot window. MCP annotations mark it as destructive.

The request is `node_id` only. If the user provides a `nodename`, first call
`get_node` to resolve exactly one node and read its `node_id` and `nodename`.
Do not ask for confirmation before this resolution step. The tool also requires
`confirm_node_id` and `confirm_nodename` to match the resolved snapshot before
calling Collector. Do not pass `nodename` as an execution selector.

Because this can reboot the node as soon as the queued action runs, the request
requires `confirmation.phrase`. The assistant must resolve the selected node,
summarize that the node will be rebooted immediately when the action is
processed, ask the user to repeat a concise phrase containing the resolved
`node_id` and `nodename` verbatim, and set `confirmation.phrase` only after that
phrase appears in the latest user message.

Required input fields:

```text
node_id
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
      "phrase": "REBOOT node NODE-ID lab-node-01"
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


### `schedule_node_reboot`

Enqueues a scheduled reboot flag action for one OpenSVC Collector node through
`PUT /actions` with `node_id=<node_id>` and `action=schedule_reboot`. This
corresponds to the Collector UI action `Reboot schedule`. It asks the OpenSVC
agent to create the local OpenSVC reboot flag on the node. The node is then
eligible for reboot by the local OpenSVC daemon scheduler at the next allowed
reboot window configured on the node, usually by the `[reboot]` section in
`node.conf`.

This tool does not accept a date, time, or delay. Requests like "in 10 minutes",
"at 16:30", or "on a specific date" are not supported by this Collector action;
the timing comes from the node OpenSVC configuration. MCP annotations mark it as
destructive because the flag can lead to a future node reboot.

The request is `node_id` only. If the user provides a `nodename`, first call
`get_node` to resolve exactly one node and read its `node_id` and `nodename`.
Do not ask for confirmation before this resolution step. The tool also requires
`confirm_node_id` and `confirm_nodename` to match the resolved snapshot before
calling Collector. Do not pass `nodename` as an execution selector.

Because this can cause a later reboot, the request requires
`confirmation.phrase`. The assistant must resolve the selected node, summarize
that the node will be marked for reboot at its next configured reboot window,
ask the user to repeat a concise phrase containing the resolved `node_id` and
`nodename` verbatim, and set `confirmation.phrase` only after that phrase appears
in the latest user message.

Required input fields:

```text
node_id
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
      "phrase": "SCHEDULE reboot node NODE-ID lab-node-01"
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


### `unschedule_node_reboot`

Enqueues a scheduled reboot cancellation action for one OpenSVC Collector node
through `PUT /actions` with `node_id=<node_id>` and
`action=unschedule_reboot`. This corresponds to the Collector UI action
`Reboot unschedule`. It asks the OpenSVC agent to remove the local scheduled
reboot flag from the node. It does not reboot or shut down the node.

The request is `node_id` only. If the user provides a `nodename`, first call
`get_node` to resolve exactly one node and read its `node_id` and `nodename`.
Do not ask for confirmation before this resolution step. The tool also requires
`confirm_node_id` and `confirm_nodename` to match the resolved snapshot before
calling Collector. Do not pass `nodename` as an execution selector.

Because this enqueues runtime work, the request requires `confirmation.phrase`.
The assistant must resolve the selected node, summarize that the scheduled
reboot flag will be removed, ask the user to repeat a concise phrase containing
the resolved `node_id` and `nodename` verbatim, and set `confirmation.phrase`
only after that phrase appears in the latest user message.

Required input fields:

```text
node_id
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
      "phrase": "UNSCHEDULE reboot node NODE-ID lab-node-01"
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

The request is `node_id` only. If the user provides a `nodename`, first call
`get_node` to resolve exactly one node and read its `node_id` and `nodename`.
Do not ask for confirmation before this resolution step. The request also
requires `confirm_node_id` and `confirm_nodename` to match the resolved
snapshot. Do not pass `nodename` as an execution selector.

Because this changes Collector alerting state, the request requires
`confirmation.phrase`. The assistant must summarize the selected node and
duration, ask the user to repeat a concise phrase containing the resolved
`node_id`, `nodename`, and duration verbatim, and set `confirmation.phrase` only
after that phrase appears in the latest user message.

Required input fields:

```text
duration
node_id
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
    "duration": "1h",
    "confirmation": {
      "phrase": "SNOOZE node NODE-ID lab-node-01 for 1h"
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

The request is `node_id` only. If the user provides a `nodename`, first call
`get_node` to resolve exactly one node and read its `node_id` and `nodename`.
Do not ask for confirmation before this resolution step. The request also
requires `confirm_node_id`, `confirm_nodename`, and `confirmation.phrase`.
Do not pass `nodename` as an execution selector.

Required input fields:

```text
node_id
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
      "phrase": "UNSNOOZE node NODE-ID lab-node-01"
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

The request is `node_id` only. If the user provides a `nodename`, first call
`get_node` to resolve exactly one node and read its `node_id` and `nodename`.
Do not ask for confirmation before this resolution step. The tool then resolves
that `node_id` back to the current `nodename` immediately before calling
Collector, because Collector applies node property updates through
`POST /nodes/<nodename>`.

The tool does not expose node creation or deletion. It accepts most fields
marked `writable=true` by the Collector nodes API definition, rejects fields
marked `writable=false` such as `node_env`, and rejects `node_id` and `nodename`
inside `properties` at the MCP boundary. Those two reserved fields are not safe
generic property updates here: `node_id` can collide with an existing node, and
renames should be handled by a dedicated sensitive rename flow. Because this
changes Collector state, the request requires `confirmation.phrase`: the
assistant must summarize the exact resolved node and property changes, ask the
user to repeat a concise phrase containing the resolved `node_id` and `nodename`
verbatim, and set `confirmation.phrase` only after that phrase appears in the
latest user message.

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
    "node_id": "NODE-ID",
    "confirm_node_id": "NODE-ID",
    "confirm_nodename": "lab-node-01",
    "properties": {
      "asset_env": "PPR"
    },
    "confirmation": {
      "phrase": "UPDATE node NODE-ID lab-node-01 asset_env PPR"
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

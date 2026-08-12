from typing import Any

from opensvc_collector_mcp.client import collector_put

from ._common import resolve_single_node_selector


DEFAULT_NODE_ACTION_SNAPSHOT_PROPS = (
    "node_id,nodename,status,node_frozen,node_frozen_at,updated"
)


async def _enqueue_node_action(
    *,
    action: str,
    operation: str,
    node_id: str | None = None,
    nodename: str | None = None,
) -> dict[str, Any]:
    selector_node_id = node_id.strip() if node_id else ""
    selector_nodename = nodename.strip() if nodename else ""

    node = await resolve_single_node_selector(
        node_id=selector_node_id or None,
        nodename=selector_nodename or None,
        props=DEFAULT_NODE_ACTION_SNAPSHOT_PROPS,
        operation=operation,
    )
    resolved_node_id = str(node.get("node_id") or "").strip()
    resolved_nodename = str(node.get("nodename") or "").strip()

    payload = {"node_id": resolved_node_id, "action": action}
    response = await collector_put("/actions", data=payload)
    return {
        "node_id": resolved_node_id,
        "nodename": resolved_nodename,
        "node": node,
        "action": action,
        "queued": True,
        "collector_response": response,
        "meta": {
            "source": "actions",
            "selector": "node_id" if selector_node_id else "nodename",
            "exec_tag": "exec:nodes",
        },
    }


async def freeze_node(
    *, node_id: str | None = None, nodename: str | None = None
) -> dict[str, Any]:
    return await _enqueue_node_action(
        action="freeze",
        operation="freeze node",
        node_id=node_id,
        nodename=nodename,
    )


async def thaw_node(
    *, node_id: str | None = None, nodename: str | None = None
) -> dict[str, Any]:
    return await _enqueue_node_action(
        action="thaw",
        operation="thaw node",
        node_id=node_id,
        nodename=nodename,
    )


async def run_node_checks(
    *, node_id: str | None = None, nodename: str | None = None
) -> dict[str, Any]:
    return await _enqueue_node_action(
        action="checks",
        operation="run node checks",
        node_id=node_id,
        nodename=nodename,
    )


async def collect_node_sysreport(
    *, node_id: str | None = None, nodename: str | None = None
) -> dict[str, Any]:
    return await _enqueue_node_action(
        action="sysreport",
        operation="collect node sysreport",
        node_id=node_id,
        nodename=nodename,
    )


async def push_node_asset(
    *, node_id: str | None = None, nodename: str | None = None
) -> dict[str, Any]:
    return await _enqueue_node_action(
        action="pushasset",
        operation="push node asset",
        node_id=node_id,
        nodename=nodename,
    )


async def push_node_disks(
    *, node_id: str | None = None, nodename: str | None = None
) -> dict[str, Any]:
    return await _enqueue_node_action(
        action="pushdisks",
        operation="push node disks",
        node_id=node_id,
        nodename=nodename,
    )


async def push_node_packages(
    *, node_id: str | None = None, nodename: str | None = None
) -> dict[str, Any]:
    return await _enqueue_node_action(
        action="pushpkg",
        operation="push node packages",
        node_id=node_id,
        nodename=nodename,
    )


async def push_node_patches(
    *, node_id: str | None = None, nodename: str | None = None
) -> dict[str, Any]:
    return await _enqueue_node_action(
        action="pushpatch",
        operation="push node patches",
        node_id=node_id,
        nodename=nodename,
    )


async def push_node_stats(
    *, node_id: str | None = None, nodename: str | None = None
) -> dict[str, Any]:
    return await _enqueue_node_action(
        action="pushstats",
        operation="push node stats",
        node_id=node_id,
        nodename=nodename,
    )


async def pull_node_config(
    *, node_id: str | None = None, nodename: str | None = None
) -> dict[str, Any]:
    return await _enqueue_node_action(
        action="pull",
        operation="pull node config",
        node_id=node_id,
        nodename=nodename,
    )


async def push_node_config(
    *, node_id: str | None = None, nodename: str | None = None
) -> dict[str, Any]:
    return await _enqueue_node_action(
        action="push",
        operation="push node config",
        node_id=node_id,
        nodename=nodename,
    )


async def update_node_compliance_modules(
    *, node_id: str | None = None, nodename: str | None = None
) -> dict[str, Any]:
    return await _enqueue_node_action(
        action="updatecomp",
        operation="update node compliance modules",
        node_id=node_id,
        nodename=nodename,
    )


async def update_node_opensvc_agent(
    *, node_id: str | None = None, nodename: str | None = None
) -> dict[str, Any]:
    return await _enqueue_node_action(
        action="updatepkg",
        operation="update node opensvc agent",
        node_id=node_id,
        nodename=nodename,
    )


async def scan_node_scsi(
    *, node_id: str | None = None, nodename: str | None = None
) -> dict[str, Any]:
    return await _enqueue_node_action(
        action="scanscsi",
        operation="scan node scsi",
        node_id=node_id,
        nodename=nodename,
    )


async def reboot_node(
    *, node_id: str | None = None, nodename: str | None = None
) -> dict[str, Any]:
    return await _enqueue_node_action(
        action="reboot",
        operation="reboot node",
        node_id=node_id,
        nodename=nodename,
    )


async def shutdown_node(
    *, node_id: str | None = None, nodename: str | None = None
) -> dict[str, Any]:
    return await _enqueue_node_action(
        action="shutdown",
        operation="shutdown node",
        node_id=node_id,
        nodename=nodename,
    )


async def schedule_node_reboot(
    *, node_id: str | None = None, nodename: str | None = None
) -> dict[str, Any]:
    return await _enqueue_node_action(
        action="schedule_reboot",
        operation="schedule node reboot",
        node_id=node_id,
        nodename=nodename,
    )


async def unschedule_node_reboot(
    *, node_id: str | None = None, nodename: str | None = None
) -> dict[str, Any]:
    return await _enqueue_node_action(
        action="unschedule_reboot",
        operation="unschedule node reboot",
        node_id=node_id,
        nodename=nodename,
    )


async def rotate_node_root_password(
    *, node_id: str | None = None, nodename: str | None = None
) -> dict[str, Any]:
    return await _enqueue_node_action(
        action="rotate_root_pw",
        operation="rotate node root password",
        node_id=node_id,
        nodename=nodename,
    )


async def wake_node_on_lan(
    *, node_id: str | None = None, nodename: str | None = None
) -> dict[str, Any]:
    return await _enqueue_node_action(
        action="wol",
        operation="wake node on lan",
        node_id=node_id,
        nodename=nodename,
    )

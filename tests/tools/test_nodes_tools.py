import pytest
from fastmcp.exceptions import ToolError

from opensvc_collector_mcp.tools import nodes as node_tools


class CoreRecorder:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def __call__(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


async def test_create_node_tool_passes_request_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder(
        {
            "nodename": "node-a",
            "submitted_properties": {"nodename": "node-a", "loc_city": "Lab City"},
            "collector_response": {"info": "node submitted"},
            "meta": {"source": "nodes"},
        }
    )
    monkeypatch.setattr(node_tools, "core_create_node", recorder)

    result = await mcp_client.call_tool(
        "create_node",
        {
            "request": {
                "nodename": "node-a",
                "properties": {"loc_city": "Lab City"},
            }
        },
    )

    assert result.structured_content["submitted_properties"] == {
        "nodename": "node-a",
        "loc_city": "Lab City",
    }
    assert recorder.calls == [
        {
            "nodename": "node-a",
            "properties": {"loc_city": "Lab City"},
        }
    ]


async def test_delete_node_tool_passes_request_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder(
        {
            "node_id": "node-a-id",
            "nodename": "node-a",
            "node": {"node_id": "node-a-id", "nodename": "node-a"},
            "deleted": True,
            "collector_response": {"info": "node deleted"},
            "meta": {"source": "nodes/<node_id>"},
        }
    )
    monkeypatch.setattr(node_tools, "core_delete_node", recorder)

    result = await mcp_client.call_tool(
        "delete_node",
        {
            "request": {
                "node_id": "node-a-id",
            }
        },
    )

    assert result.structured_content["deleted"] is True
    assert result.structured_content["node_id"] == "node-a-id"
    assert recorder.calls == [
        {
            "node_id": "node-a-id",
            "nodename": None,
        }
    ]


async def test_delete_node_tool_rejects_nodename_selector(monkeypatch, mcp_client):
    recorder = CoreRecorder({})
    monkeypatch.setattr(node_tools, "core_delete_node", recorder)

    with pytest.raises(ToolError) as exc_info:
        await mcp_client.call_tool(
            "delete_node",
            {
                "request": {
                    "nodename": "node-a",
                }
            },
        )

    assert '"loc": ["request", "node_id"]' in str(exc_info.value)
    assert '"loc": ["request", "nodename"]' in str(exc_info.value)
    assert recorder.calls == []


async def test_freeze_node_tool_passes_request_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder(
        {
            "node_id": "node-a-id",
            "nodename": "node-a",
            "node": {"node_id": "node-a-id", "nodename": "node-a"},
            "action": "freeze",
            "queued": True,
            "collector_response": {"info": "action queued"},
            "meta": {"source": "actions", "exec_tag": "exec:nodes"},
        }
    )
    monkeypatch.setattr(node_tools, "core_freeze_node", recorder)

    result = await mcp_client.call_tool(
        "freeze_node",
        {
            "request": {
                "node_id": "node-a-id",
            }
        },
    )

    assert result.structured_content["queued"] is True
    assert result.structured_content["action"] == "freeze"
    assert recorder.calls == [
        {
            "node_id": "node-a-id",
            "nodename": None,
        }
    ]


async def test_thaw_node_tool_passes_request_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder(
        {
            "node_id": "node-a-id",
            "nodename": "node-a",
            "node": {"node_id": "node-a-id", "nodename": "node-a"},
            "action": "thaw",
            "queued": True,
            "collector_response": {"info": "action queued"},
            "meta": {"source": "actions", "exec_tag": "exec:nodes"},
        }
    )
    monkeypatch.setattr(node_tools, "core_thaw_node", recorder)

    result = await mcp_client.call_tool(
        "thaw_node",
        {
            "request": {
                "node_id": "node-a-id",
            }
        },
    )

    assert result.structured_content["queued"] is True
    assert result.structured_content["action"] == "thaw"
    assert recorder.calls == [
        {
            "node_id": "node-a-id",
            "nodename": None,
        }
    ]


@pytest.mark.parametrize(
    ("tool_name", "core_attr", "action"),
    [
        ("run_node_checks", "core_run_node_checks", "checks"),
        ("collect_node_sysreport", "core_collect_node_sysreport", "sysreport"),
        ("push_node_asset", "core_push_node_asset", "pushasset"),
        ("push_node_disks", "core_push_node_disks", "pushdisks"),
        ("push_node_packages", "core_push_node_packages", "pushpkg"),
        ("push_node_patches", "core_push_node_patches", "pushpatch"),
        ("push_node_stats", "core_push_node_stats", "pushstats"),
        ("pull_node_config", "core_pull_node_config", "pull"),
        ("push_node_config", "core_push_node_config", "push"),
        ("update_node_compliance_modules", "core_update_node_compliance_modules", "updatecomp"),
        ("update_node_opensvc_agent", "core_update_node_opensvc_agent", "updatepkg"),
        ("scan_node_scsi", "core_scan_node_scsi", "scanscsi"),
        ("reboot_node", "core_reboot_node", "reboot"),
        ("shutdown_node", "core_shutdown_node", "shutdown"),
        ("schedule_node_reboot", "core_schedule_node_reboot", "schedule_reboot"),
        ("unschedule_node_reboot", "core_unschedule_node_reboot", "unschedule_reboot"),
        ("rotate_node_root_password", "core_rotate_node_root_password", "rotate_root_pw"),
        ("wake_node_on_lan", "core_wake_node_on_lan", "wol"),
    ],
)
async def test_node_exec_action_tool_passes_request_to_core(
    monkeypatch,
    mcp_client,
    tool_name,
    core_attr,
    action,
):
    recorder = CoreRecorder(
        {
            "node_id": "node-a-id",
            "nodename": "node-a",
            "node": {"node_id": "node-a-id", "nodename": "node-a"},
            "action": action,
            "queued": True,
            "collector_response": {"info": "action queued"},
            "meta": {"source": "actions", "exec_tag": "exec:nodes"},
        }
    )
    monkeypatch.setattr(node_tools, core_attr, recorder)

    result = await mcp_client.call_tool(
        tool_name,
        {
            "request": {
                "node_id": "node-a-id",
            }
        },
    )

    assert result.structured_content["queued"] is True
    assert result.structured_content["action"] == action
    assert recorder.calls == [
        {
            "node_id": "node-a-id",
            "nodename": None,
        }
    ]


@pytest.mark.parametrize(
    ("tool_name", "core_attr"),
    [
        ("freeze_node", "core_freeze_node"),
        ("thaw_node", "core_thaw_node"),
        ("run_node_checks", "core_run_node_checks"),
        ("collect_node_sysreport", "core_collect_node_sysreport"),
        ("push_node_asset", "core_push_node_asset"),
        ("push_node_disks", "core_push_node_disks"),
        ("push_node_packages", "core_push_node_packages"),
        ("push_node_patches", "core_push_node_patches"),
        ("push_node_stats", "core_push_node_stats"),
        ("pull_node_config", "core_pull_node_config"),
        ("push_node_config", "core_push_node_config"),
        ("update_node_compliance_modules", "core_update_node_compliance_modules"),
        ("update_node_opensvc_agent", "core_update_node_opensvc_agent"),
        ("scan_node_scsi", "core_scan_node_scsi"),
        ("reboot_node", "core_reboot_node"),
        ("shutdown_node", "core_shutdown_node"),
        ("schedule_node_reboot", "core_schedule_node_reboot"),
        ("unschedule_node_reboot", "core_unschedule_node_reboot"),
        ("rotate_node_root_password", "core_rotate_node_root_password"),
        ("wake_node_on_lan", "core_wake_node_on_lan"),
    ],
)
async def test_node_exec_action_tools_reject_nodename_selector(
    monkeypatch,
    mcp_client,
    tool_name,
    core_attr,
):
    recorder = CoreRecorder({})
    monkeypatch.setattr(node_tools, core_attr, recorder)

    with pytest.raises(ToolError) as exc_info:
        await mcp_client.call_tool(
            tool_name,
            {
                "request": {
                    "nodename": "node-a",
                }
            },
        )

    assert '"loc": ["request", "node_id"]' in str(exc_info.value)
    assert '"loc": ["request", "nodename"]' in str(exc_info.value)
    assert recorder.calls == []


async def test_update_node_properties_tool_passes_request_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder(
        {
            "nodename": "node-a",
            "updated_properties": {"loc_city": "Lab City"},
            "collector_response": {"info": "node updated"},
            "meta": {"source": "nodes/<nodename>"},
        }
    )
    monkeypatch.setattr(node_tools, "core_update_node_properties", recorder)

    result = await mcp_client.call_tool(
        "update_node_properties",
        {
            "request": {
                "node_id": "node-a-id",
                "properties": {"loc_city": "Lab City"},
            }
        },
    )

    assert result.structured_content["updated_properties"] == {"loc_city": "Lab City"}
    assert recorder.calls == [
        {
            "node_id": "node-a-id",
            "nodename": None,
            "properties": {"loc_city": "Lab City"},
        }
    ]


async def test_update_node_properties_tool_rejects_nodename_selector(
    monkeypatch,
    mcp_client,
):
    recorder = CoreRecorder({})
    monkeypatch.setattr(node_tools, "core_update_node_properties", recorder)

    with pytest.raises(ToolError) as exc_info:
        await mcp_client.call_tool(
            "update_node_properties",
            {
                "request": {
                    "nodename": "node-a",
                    "properties": {"loc_city": "Lab City"},
                }
            },
        )

    assert '"loc": ["request", "node_id"]' in str(exc_info.value)
    assert '"loc": ["request", "nodename"]' in str(exc_info.value)
    assert recorder.calls == []


async def test_snooze_node_notifications_tool_passes_request_to_core(
    monkeypatch,
    mcp_client,
):
    recorder = CoreRecorder(
        {
            "node_id": "node-a-id",
            "nodename": "node-a",
            "duration": "1h",
            "node": {"node_id": "node-a-id", "nodename": "node-a"},
            "snoozed": True,
            "collector_response": {"info": "snoozed"},
            "meta": {"source": "nodes/<node_id>/snooze"},
        }
    )
    monkeypatch.setattr(node_tools, "core_snooze_node_notifications", recorder)

    result = await mcp_client.call_tool(
        "snooze_node_notifications",
        {
            "request": {
                "node_id": "node-a-id",
                "duration": "1h",
            }
        },
    )

    assert result.structured_content["snoozed"] is True
    assert result.structured_content["duration"] == "1h"
    assert recorder.calls == [
        {
            "node_id": "node-a-id",
            "nodename": None,
            "duration": "1h",
        }
    ]


async def test_unsnooze_node_notifications_tool_passes_request_to_core(
    monkeypatch,
    mcp_client,
):
    recorder = CoreRecorder(
        {
            "node_id": "node-a-id",
            "nodename": "node-a",
            "node": {"node_id": "node-a-id", "nodename": "node-a"},
            "unsnoozed": True,
            "collector_response": {"info": "unsnoozed"},
            "meta": {"source": "nodes/<node_id>/snooze"},
        }
    )
    monkeypatch.setattr(node_tools, "core_unsnooze_node_notifications", recorder)

    result = await mcp_client.call_tool(
        "unsnooze_node_notifications",
        {
            "request": {
                "node_id": "node-a-id",
            }
        },
    )

    assert result.structured_content["unsnoozed"] is True
    assert recorder.calls == [
        {
            "node_id": "node-a-id",
            "nodename": None,
        }
    ]


@pytest.mark.parametrize(
    ("tool_name", "core_attr", "extra_fields"),
    [
        (
            "snooze_node_notifications",
            "core_snooze_node_notifications",
            {"duration": "1h"},
        ),
        (
            "unsnooze_node_notifications",
            "core_unsnooze_node_notifications",
            {},
        ),
    ],
)
async def test_node_notification_tools_reject_nodename_selector(
    monkeypatch,
    mcp_client,
    tool_name,
    core_attr,
    extra_fields,
):
    recorder = CoreRecorder({})
    monkeypatch.setattr(node_tools, core_attr, recorder)

    with pytest.raises(ToolError) as exc_info:
        await mcp_client.call_tool(
            tool_name,
            {
                "request": {
                    "nodename": "node-a",
                    **extra_fields,
                }
            },
        )

    assert '"loc": ["request", "node_id"]' in str(exc_info.value)
    assert '"loc": ["request", "nodename"]' in str(exc_info.value)
    assert recorder.calls == []


async def test_list_nodes_tool_passes_request_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder(
        {
            "pagination": {
                "limit": 5,
                "offset": 2,
                "returned": 1,
                "next_offset": None,
                "complete": True,
            },
            "data": [{"nodename": "node-a"}],
        }
    )
    monkeypatch.setattr(node_tools, "core_list_nodes", recorder)

    result = await mcp_client.call_tool(
        "list_nodes",
        {
            "request": {
                "status": "up",
                "props": "nodename,status",
                "orderby": "nodename",
                "search": "node-a",
                "limit": 5,
                "offset": 2,
            }
        },
    )

    assert result.structured_content["pagination"]["complete"] is True
    assert result.structured_content["data"] == [{"nodename": "node-a"}]
    assert recorder.calls == [
        {
            "filters": {"status": "up"},
            "props": "nodename,status",
            "orderby": "nodename",
            "search": "node-a",
            "limit": 5,
            "offset": 2,
            "nodename_contains": None,
            "max_scan": 5000,
        }
    ]


async def test_count_nodes_tool_passes_merged_filters_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder({"count": 3, "filters": {"status": "up"}})
    monkeypatch.setattr(node_tools, "core_count_nodes", recorder)

    result = await mcp_client.call_tool(
        "count_nodes",
        {"request": {"status": "up"}},
    )

    assert result.structured_content == {"count": 3, "filters": {"status": "up"}}
    assert recorder.calls == [{"filters": {"status": "up"}}]


async def test_get_node_tool_passes_nodename_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder({"meta": {}, "data": [{"nodename": "node-a"}]})
    monkeypatch.setattr(node_tools, "core_get_node", recorder)

    result = await mcp_client.call_tool(
        "get_node",
        {"request": {"nodename": "node-a"}},
    )

    assert result.structured_content == {"meta": {}, "data": [{"nodename": "node-a"}]}
    assert recorder.calls == [{"nodename": "node-a"}]


async def test_get_node_disks_tool_passes_relation_request_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder(
        {
            "nodename": "node-a",
            "pagination": {
                "limit": 4,
                "offset": 1,
                "returned": 1,
                "next_offset": None,
                "complete": True,
            },
            "data": [{"disk_id": "DISK-ID"}],
        }
    )
    monkeypatch.setattr(node_tools, "core_get_node_disks", recorder)

    result = await mcp_client.call_tool(
        "get_node_disks",
        {
            "request": {
                "nodename": "node-a",
                "filters": {"disk_local": "false"},
                "props": "disk_id,disk_size",
                "limit": 4,
                "offset": 1,
            }
        },
    )

    assert result.structured_content["data"][0]["disk_id"] == "DISK-ID"
    assert recorder.calls == [
        {
            "nodename": "node-a",
            "filters": {"disk_local": "false"},
            "props": "disk_id,disk_size",
            "orderby": None,
            "search": None,
            "limit": 4,
            "offset": 1,
        }
    ]


async def test_get_node_services_tool_passes_relation_request_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder(
        {
            "nodename": "node-a",
            "pagination": {
                "limit": 3,
                "offset": 0,
                "returned": 1,
                "next_offset": None,
                "complete": True,
            },
            "data": [{"svcname": "svc-a"}],
        }
    )
    monkeypatch.setattr(node_tools, "core_get_node_services", recorder)

    result = await mcp_client.call_tool(
        "get_node_services",
        {
            "request": {
                "nodename": "node-a",
                "filters": {"services.svc_status": "up"},
                "props": "services.svcname:svcname",
                "limit": 3,
            }
        },
    )

    assert result.structured_content["data"][0]["svcname"] == "svc-a"
    assert recorder.calls == [
        {
            "nodename": "node-a",
            "filters": {"services.svc_status": "up"},
            "props": "services.svcname:svcname",
            "orderby": None,
            "search": None,
            "limit": 3,
            "offset": 0,
        }
    ]

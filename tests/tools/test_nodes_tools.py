import pytest

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
                "confirmation": {"phrase": "CREATE node node-a loc_city Lab City"},
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
                "confirm_node_id": "node-a-id",
                "confirm_nodename": "node-a",
                "confirmation": {"phrase": "DELETE node node-a-id node-a"},
            }
        },
    )

    assert result.structured_content["deleted"] is True
    assert result.structured_content["node_id"] == "node-a-id"
    assert recorder.calls == [
        {
            "node_id": "node-a-id",
            "nodename": None,
            "confirm_node_id": "node-a-id",
            "confirm_nodename": "node-a",
        }
    ]


async def test_delete_node_tool_accepts_nodename_selector(monkeypatch, mcp_client):
    recorder = CoreRecorder(
        {
            "node_id": "node-a-id",
            "nodename": "node-a",
            "node": {"node_id": "node-a-id", "nodename": "node-a"},
            "deleted": True,
            "collector_response": {"info": "node deleted"},
            "meta": {"source": "nodes/<node_id>", "selector": "nodename"},
        }
    )
    monkeypatch.setattr(node_tools, "core_delete_node", recorder)

    result = await mcp_client.call_tool(
        "delete_node",
        {
            "request": {
                "nodename": "node-a",
                "confirm_node_id": "node-a-id",
                "confirm_nodename": "node-a",
                "confirmation": {"phrase": "DELETE node node-a-id node-a"},
            }
        },
    )

    assert result.structured_content["deleted"] is True
    assert recorder.calls == [
        {
            "node_id": None,
            "nodename": "node-a",
            "confirm_node_id": "node-a-id",
            "confirm_nodename": "node-a",
        }
    ]


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
                "confirm_node_id": "node-a-id",
                "confirm_nodename": "node-a",
                "confirmation": {"phrase": "FREEZE node node-a-id node-a"},
            }
        },
    )

    assert result.structured_content["queued"] is True
    assert result.structured_content["action"] == "freeze"
    assert recorder.calls == [
        {
            "node_id": "node-a-id",
            "nodename": None,
            "confirm_node_id": "node-a-id",
            "confirm_nodename": "node-a",
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
                "confirm_node_id": "node-a-id",
                "confirm_nodename": "node-a",
                "confirmation": {"phrase": "THAW node node-a-id node-a"},
            }
        },
    )

    assert result.structured_content["queued"] is True
    assert result.structured_content["action"] == "thaw"
    assert recorder.calls == [
        {
            "node_id": "node-a-id",
            "nodename": None,
            "confirm_node_id": "node-a-id",
            "confirm_nodename": "node-a",
        }
    ]


@pytest.mark.parametrize(
    ("tool_name", "core_attr", "action", "phrase"),
    [
        ("run_node_checks", "core_run_node_checks", "checks", "RUN checks node node-a-id node-a"),
        (
            "collect_node_sysreport",
            "core_collect_node_sysreport",
            "sysreport",
            "COLLECT sysreport node node-a-id node-a",
        ),
        (
            "push_node_asset",
            "core_push_node_asset",
            "pushasset",
            "PUSH asset node node-a-id node-a",
        ),
    ],
)
async def test_node_exec_action_tool_passes_request_to_core(
    monkeypatch,
    mcp_client,
    tool_name,
    core_attr,
    action,
    phrase,
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
                "confirm_node_id": "node-a-id",
                "confirm_nodename": "node-a",
                "confirmation": {"phrase": phrase},
            }
        },
    )

    assert result.structured_content["queued"] is True
    assert result.structured_content["action"] == action
    assert recorder.calls == [
        {
            "node_id": "node-a-id",
            "nodename": None,
            "confirm_node_id": "node-a-id",
            "confirm_nodename": "node-a",
        }
    ]


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
                "nodename": "node-a",
                "properties": {"loc_city": "Lab City"},
                "confirmation": {"phrase": "UPDATE node node-a loc_city Lab City"},
            }
        },
    )

    assert result.structured_content["updated_properties"] == {"loc_city": "Lab City"}
    assert recorder.calls == [
        {
            "nodename": "node-a",
            "properties": {"loc_city": "Lab City"},
        }
    ]


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
                "nodename": "node-a",
                "duration": "1h",
                "confirmation": {"phrase": "SNOOZE node node-a for 1h"},
            }
        },
    )

    assert result.structured_content["snoozed"] is True
    assert result.structured_content["duration"] == "1h"
    assert recorder.calls == [
        {"node_id": None, "nodename": "node-a", "duration": "1h"}
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
                "confirmation": {"phrase": "UNSNOOZE node node-a-id"},
            }
        },
    )

    assert result.structured_content["unsnoozed"] is True
    assert recorder.calls == [{"node_id": "node-a-id", "nodename": None}]


async def test_list_nodes_tool_passes_request_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder({"meta": {"total": 1}, "data": [{"nodename": "node-a"}]})
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

    assert result.structured_content == {"meta": {"total": 1}, "data": [{"nodename": "node-a"}]}
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
        {"nodename": "node-a", "meta": {"total": 1}, "data": [{"disk_id": "DISK-ID"}]}
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
        {"nodename": "node-a", "meta": {"total": 1}, "data": [{"svcname": "svc-a"}]}
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

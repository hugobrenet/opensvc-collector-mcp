import pytest

from opensvc_collector_mcp.core.nodes import inventory, services, storage
from opensvc_collector_mcp.core.nodes import _common as node_common
from opensvc_collector_mcp.models.nodes.storage import NodeDisksResponse


class CollectorPostRecorder:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def __call__(self, path, data=None, params=None):
        self.calls.append({"path": path, "data": data, "params": params})
        return self.response


class CollectorPutRecorder:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def __call__(self, path, data=None, params=None):
        self.calls.append({"path": path, "data": data, "params": params})
        return self.response


class CollectorDeleteRecorder:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def __call__(self, path, data=None, params=None):
        self.calls.append({"path": path, "data": data, "params": params})
        return self.response


@pytest.mark.parametrize("raw, expected", [(" node-a ", "/nodes/node-a"), ("node/a", "/nodes/node%2Fa")])
async def test_get_node_uses_node_detail_endpoint(monkeypatch, collector_mock_factory, raw, expected):
    collector = collector_mock_factory([{"meta": {}, "data": [{"nodename": "node-a"}]}])
    monkeypatch.setattr(inventory, "collector_get", collector.get)

    response = await inventory.get_node(raw)

    assert response["data"] == [{"nodename": "node-a"}]
    assert collector.calls[0].path == expected
    assert collector.calls[0].params is None


async def test_delete_node_snapshots_confirms_and_deletes_by_node_id(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [
            {
                "meta": {},
                "data": [
                    {
                        "node_id": "node/id",
                        "nodename": "node-a",
                        "status": "up",
                    }
                ],
            }
        ]
    )
    delete_recorder = CollectorDeleteRecorder({"info": "node deleted"})
    monkeypatch.setattr(node_common, "collector_get", collector.get)
    monkeypatch.setattr(inventory, "collector_delete", delete_recorder)

    response = await inventory.delete_node(
        node_id=" node/id ",
        confirm_node_id="node/id",
        confirm_nodename=" node-a ",
    )

    assert response["deleted"] is True
    assert response["node_id"] == "node/id"
    assert response["nodename"] == "node-a"
    assert response["node"]["node_id"] == "node/id"
    assert response["collector_response"] == {"info": "node deleted"}
    assert collector.calls[0].path == "/nodes/node%2Fid"
    assert collector.calls[0].params == {
        "props": inventory.DEFAULT_NODE_DELETE_SNAPSHOT_PROPS
    }
    assert delete_recorder.calls == [
        {"path": "/nodes/node%2Fid", "data": None, "params": None}
    ]


async def test_delete_node_resolves_nodename_confirms_and_deletes_by_node_id(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [
            {
                "meta": {"total": 1},
                "data": [
                    {
                        "node_id": "node/id",
                        "nodename": "node-a",
                        "status": "up",
                    }
                ],
            }
        ]
    )
    delete_recorder = CollectorDeleteRecorder({"info": "node deleted"})
    monkeypatch.setattr(node_common, "collector_get", collector.get)
    monkeypatch.setattr(inventory, "collector_delete", delete_recorder)

    response = await inventory.delete_node(
        nodename=" node-a ",
        confirm_node_id="node/id",
        confirm_nodename=" node-a ",
    )

    assert response["deleted"] is True
    assert response["node_id"] == "node/id"
    assert response["nodename"] == "node-a"
    assert response["meta"]["selector"] == "nodename"
    assert collector.calls[0].path == "/nodes"
    assert collector.calls[0].single_param("props") == inventory.DEFAULT_NODE_DELETE_SNAPSHOT_PROPS
    assert collector.calls[0].single_param("limit") == 2
    assert collector.calls[0].param_values("filters") == ["nodename=node-a"]
    assert delete_recorder.calls == [
        {"path": "/nodes/node%2Fid", "data": None, "params": None}
    ]


async def test_delete_node_rejects_confirmation_id_mismatch_before_lookup(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory([])
    delete_recorder = CollectorDeleteRecorder({"info": "node deleted"})
    monkeypatch.setattr(node_common, "collector_get", collector.get)
    monkeypatch.setattr(inventory, "collector_delete", delete_recorder)

    with pytest.raises(ValueError, match="confirm_node_id must match node_id"):
        await inventory.delete_node(
            node_id="node-a-id",
            confirm_node_id="other-node-id",
            confirm_nodename="node-a",
        )

    assert collector.calls == []
    assert delete_recorder.calls == []


async def test_delete_node_rejects_confirmation_name_mismatch_before_delete(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [{"meta": {}, "data": [{"node_id": "node-a-id", "nodename": "node-a"}]}]
    )
    delete_recorder = CollectorDeleteRecorder({"info": "node deleted"})
    monkeypatch.setattr(node_common, "collector_get", collector.get)
    monkeypatch.setattr(inventory, "collector_delete", delete_recorder)

    with pytest.raises(ValueError, match="confirm_nodename must match"):
        await inventory.delete_node(
            node_id="node-a-id",
            confirm_node_id="node-a-id",
            confirm_nodename="node-b",
        )

    assert len(collector.calls) == 1
    assert delete_recorder.calls == []


async def test_delete_node_rejects_ambiguous_node_id_snapshot(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [
            {
                "meta": {},
                "data": [
                    {"node_id": "node-a-id", "nodename": "node-a"},
                    {"node_id": "node-a-id", "nodename": "node-a-copy"},
                ],
            }
        ]
    )
    delete_recorder = CollectorDeleteRecorder({"info": "node deleted"})
    monkeypatch.setattr(node_common, "collector_get", collector.get)
    monkeypatch.setattr(inventory, "collector_delete", delete_recorder)

    with pytest.raises(ValueError, match="node_id resolved to multiple nodes"):
        await inventory.delete_node(
            node_id="node-a-id",
            confirm_node_id="node-a-id",
            confirm_nodename="node-a",
        )

    assert delete_recorder.calls == []


async def test_delete_node_rejects_ambiguous_nodename_before_delete(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [
            {
                "meta": {"total": 2},
                "data": [
                    {"node_id": "node-a-id", "nodename": "node-a"},
                    {"node_id": "node-b-id", "nodename": "node-a"},
                ],
            }
        ]
    )
    delete_recorder = CollectorDeleteRecorder({"info": "node deleted"})
    monkeypatch.setattr(node_common, "collector_get", collector.get)
    monkeypatch.setattr(inventory, "collector_delete", delete_recorder)

    with pytest.raises(ValueError, match="nodename is ambiguous: node-a"):
        await inventory.delete_node(
            nodename="node-a",
            confirm_node_id="node-a-id",
            confirm_nodename="node-a",
        )

    assert delete_recorder.calls == []


async def test_delete_node_rejects_nodename_passed_as_node_id(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [
            {
                "meta": {},
                "data": [
                    {
                        "node_id": "real-node-id",
                        "nodename": "node-a",
                    }
                ],
            }
        ]
    )
    delete_recorder = CollectorDeleteRecorder({"info": "node deleted"})
    monkeypatch.setattr(node_common, "collector_get", collector.get)
    monkeypatch.setattr(inventory, "collector_delete", delete_recorder)

    with pytest.raises(ValueError, match="node_id selector did not resolve to the exact node_id"):
        await inventory.delete_node(
            node_id="node-a",
            confirm_node_id="node-a",
            confirm_nodename="node-a",
        )

    assert collector.calls[0].path == "/nodes/node-a"
    assert delete_recorder.calls == []


async def test_freeze_node_resolves_nodename_confirms_and_enqueues_action(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [
            {
                "meta": {"total": 1},
                "data": [
                    {
                        "node_id": "node/id",
                        "nodename": "node-a",
                        "status": "up",
                        "node_frozen": None,
                    }
                ],
            }
        ]
    )
    put_recorder = CollectorPutRecorder({"info": "action queued"})
    monkeypatch.setattr(node_common, "collector_get", collector.get)
    monkeypatch.setattr(inventory, "collector_put", put_recorder)

    response = await inventory.freeze_node(
        nodename=" node-a ",
        confirm_node_id="node/id",
        confirm_nodename=" node-a ",
    )

    assert response["queued"] is True
    assert response["action"] == "freeze"
    assert response["node_id"] == "node/id"
    assert response["nodename"] == "node-a"
    assert response["meta"]["exec_tag"] == "exec:nodes"
    assert collector.calls[0].path == "/nodes"
    assert collector.calls[0].single_param("props") == inventory.DEFAULT_NODE_ACTION_SNAPSHOT_PROPS
    assert collector.calls[0].single_param("limit") == 2
    assert collector.calls[0].param_values("filters") == ["nodename=node-a"]
    assert put_recorder.calls == [
        {
            "path": "/actions",
            "data": {"node_id": "node/id", "action": "freeze"},
            "params": None,
        }
    ]


async def test_freeze_node_resolves_node_id_confirms_and_enqueues_action(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [
            {
                "meta": {},
                "data": [
                    {
                        "node_id": "node/id",
                        "nodename": "node-a",
                        "status": "up",
                    }
                ],
            }
        ]
    )
    put_recorder = CollectorPutRecorder({"info": "action queued"})
    monkeypatch.setattr(node_common, "collector_get", collector.get)
    monkeypatch.setattr(inventory, "collector_put", put_recorder)

    response = await inventory.freeze_node(
        node_id=" node/id ",
        confirm_node_id="node/id",
        confirm_nodename="node-a",
    )

    assert response["node_id"] == "node/id"
    assert response["meta"]["selector"] == "node_id"
    assert collector.calls[0].path == "/nodes/node%2Fid"
    assert put_recorder.calls == [
        {
            "path": "/actions",
            "data": {"node_id": "node/id", "action": "freeze"},
            "params": None,
        }
    ]


async def test_freeze_node_rejects_confirmation_mismatch_before_enqueue(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [
            {
                "meta": {},
                "data": [{"node_id": "node-a-id", "nodename": "node-a"}],
            }
        ]
    )
    put_recorder = CollectorPutRecorder({"info": "action queued"})
    monkeypatch.setattr(node_common, "collector_get", collector.get)
    monkeypatch.setattr(inventory, "collector_put", put_recorder)

    with pytest.raises(ValueError, match="confirm_nodename must match"):
        await inventory.freeze_node(
            node_id="node-a-id",
            confirm_node_id="node-a-id",
            confirm_nodename="node-b",
        )

    assert len(collector.calls) == 1
    assert put_recorder.calls == []


async def test_freeze_node_requires_exactly_one_selector(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory([])
    put_recorder = CollectorPutRecorder({"info": "action queued"})
    monkeypatch.setattr(node_common, "collector_get", collector.get)
    monkeypatch.setattr(inventory, "collector_put", put_recorder)

    with pytest.raises(ValueError, match="requires exactly one node selector"):
        await inventory.freeze_node(
            node_id="node-a-id",
            nodename="node-a",
            confirm_node_id="node-a-id",
            confirm_nodename="node-a",
        )

    assert collector.calls == []
    assert put_recorder.calls == []


async def test_thaw_node_resolves_nodename_confirms_and_enqueues_action(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [
            {
                "meta": {"total": 1},
                "data": [
                    {
                        "node_id": "node/id",
                        "nodename": "node-a",
                        "status": "up",
                        "node_frozen": True,
                    }
                ],
            }
        ]
    )
    put_recorder = CollectorPutRecorder({"info": "action queued"})
    monkeypatch.setattr(node_common, "collector_get", collector.get)
    monkeypatch.setattr(inventory, "collector_put", put_recorder)

    response = await inventory.thaw_node(
        nodename=" node-a ",
        confirm_node_id="node/id",
        confirm_nodename=" node-a ",
    )

    assert response["queued"] is True
    assert response["action"] == "thaw"
    assert response["node_id"] == "node/id"
    assert response["nodename"] == "node-a"
    assert response["meta"]["exec_tag"] == "exec:nodes"
    assert collector.calls[0].path == "/nodes"
    assert collector.calls[0].single_param("props") == inventory.DEFAULT_NODE_ACTION_SNAPSHOT_PROPS
    assert collector.calls[0].single_param("limit") == 2
    assert collector.calls[0].param_values("filters") == ["nodename=node-a"]
    assert put_recorder.calls == [
        {
            "path": "/actions",
            "data": {"node_id": "node/id", "action": "thaw"},
            "params": None,
        }
    ]


async def test_thaw_node_requires_exactly_one_selector(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory([])
    put_recorder = CollectorPutRecorder({"info": "action queued"})
    monkeypatch.setattr(node_common, "collector_get", collector.get)
    monkeypatch.setattr(inventory, "collector_put", put_recorder)

    with pytest.raises(ValueError, match="requires exactly one node selector"):
        await inventory.thaw_node(
            node_id="node-a-id",
            nodename="node-a",
            confirm_node_id="node-a-id",
            confirm_nodename="node-a",
        )

    assert collector.calls == []
    assert put_recorder.calls == []


@pytest.mark.parametrize(
    ("function_name", "expected_action"),
    [
        ("run_node_checks", "checks"),
        ("collect_node_sysreport", "sysreport"),
        ("push_node_asset", "pushasset"),
        ("push_node_disks", "pushdisks"),
        ("push_node_packages", "pushpkg"),
        ("push_node_patches", "pushpatch"),
        ("push_node_stats", "pushstats"),
        ("pull_node_config", "pull"),
        ("push_node_config", "push"),
        ("update_node_compliance_modules", "updatecomp"),
        ("update_node_opensvc_agent", "updatepkg"),
    ],
)
async def test_node_exec_action_resolves_nodename_confirms_and_enqueues_action(
    monkeypatch,
    collector_mock_factory,
    function_name,
    expected_action,
):
    collector = collector_mock_factory(
        [
            {
                "meta": {"total": 1},
                "data": [
                    {
                        "node_id": "node/id",
                        "nodename": "node-a",
                        "status": "up",
                        "node_frozen": False,
                    }
                ],
            }
        ]
    )
    put_recorder = CollectorPutRecorder({"info": "action queued"})
    monkeypatch.setattr(node_common, "collector_get", collector.get)
    monkeypatch.setattr(inventory, "collector_put", put_recorder)

    function = getattr(inventory, function_name)
    response = await function(
        nodename=" node-a ",
        confirm_node_id="node/id",
        confirm_nodename=" node-a ",
    )

    assert response["queued"] is True
    assert response["action"] == expected_action
    assert response["node_id"] == "node/id"
    assert response["nodename"] == "node-a"
    assert response["meta"]["exec_tag"] == "exec:nodes"
    assert collector.calls[0].path == "/nodes"
    assert collector.calls[0].single_param("props") == inventory.DEFAULT_NODE_ACTION_SNAPSHOT_PROPS
    assert collector.calls[0].single_param("limit") == 2
    assert collector.calls[0].param_values("filters") == ["nodename=node-a"]
    assert put_recorder.calls == [
        {
            "path": "/actions",
            "data": {"node_id": "node/id", "action": expected_action},
            "params": None,
        }
    ]


async def test_run_node_checks_requires_exactly_one_selector(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory([])
    put_recorder = CollectorPutRecorder({"info": "action queued"})
    monkeypatch.setattr(node_common, "collector_get", collector.get)
    monkeypatch.setattr(inventory, "collector_put", put_recorder)

    with pytest.raises(ValueError, match="requires exactly one node selector"):
        await inventory.run_node_checks(
            node_id="node-a-id",
            nodename="node-a",
            confirm_node_id="node-a-id",
            confirm_nodename="node-a",
        )

    assert collector.calls == []
    assert put_recorder.calls == []


async def test_snooze_node_notifications_resolves_nodename_then_posts_node_id(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [
            {
                "meta": {"total": 1},
                "data": [
                    {
                        "node_id": "node/id",
                        "nodename": "node-a",
                        "status": "up",
                        "snooze_till": None,
                    }
                ],
            }
        ]
    )
    recorder = CollectorPostRecorder({"info": "snoozed"})
    monkeypatch.setattr(node_common, "collector_get", collector.get)
    monkeypatch.setattr(inventory, "collector_post", recorder)

    response = await inventory.snooze_node_notifications(
        nodename=" node-a ",
        duration=" 1h ",
    )

    assert response["node_id"] == "node/id"
    assert response["nodename"] == "node-a"
    assert response["duration"] == "1h"
    assert response["snoozed"] is True
    assert collector.calls[0].path == "/nodes"
    assert collector.calls[0].single_param("props") == inventory.DEFAULT_NODE_SNOOZE_SNAPSHOT_PROPS
    assert collector.calls[0].single_param("limit") == 2
    assert collector.calls[0].param_values("filters") == ["nodename=node-a"]
    assert recorder.calls == [
        {
            "path": "/nodes/node%2Fid/snooze",
            "data": {"duration": "1h"},
            "params": None,
        }
    ]


async def test_unsnooze_node_notifications_resolves_node_id_then_posts_without_duration(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [
            {
                "meta": {},
                "data": [
                    {
                        "node_id": "node/id",
                        "nodename": "node-a",
                        "status": "up",
                        "snooze_till": "2026-06-15 20:00:00",
                    }
                ],
            }
        ]
    )
    recorder = CollectorPostRecorder({"info": "unsnoozed"})
    monkeypatch.setattr(node_common, "collector_get", collector.get)
    monkeypatch.setattr(inventory, "collector_post", recorder)

    response = await inventory.unsnooze_node_notifications(node_id=" node/id ")

    assert response["node_id"] == "node/id"
    assert response["nodename"] == "node-a"
    assert response["unsnoozed"] is True
    assert collector.calls[0].path == "/nodes/node%2Fid"
    assert collector.calls[0].params == {"props": inventory.DEFAULT_NODE_SNOOZE_SNAPSHOT_PROPS}
    assert recorder.calls == [
        {"path": "/nodes/node%2Fid/snooze", "data": None, "params": None}
    ]


async def test_snooze_node_notifications_rejects_ambiguous_nodename(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [
            {
                "meta": {"total": 2},
                "data": [
                    {"node_id": "node-a-id", "nodename": "node-a"},
                    {"node_id": "node-b-id", "nodename": "node-a"},
                ],
            }
        ]
    )
    recorder = CollectorPostRecorder({"info": "snoozed"})
    monkeypatch.setattr(node_common, "collector_get", collector.get)
    monkeypatch.setattr(inventory, "collector_post", recorder)

    with pytest.raises(ValueError, match="nodename is ambiguous: node-a"):
        await inventory.snooze_node_notifications(nodename="node-a", duration="1h")

    assert recorder.calls == []


@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"node_id": "node-a-id", "nodename": "node-a"},
    ],
)
async def test_snooze_node_notifications_requires_exactly_one_selector(
    monkeypatch,
    collector_mock_factory,
    kwargs,
):
    collector = collector_mock_factory([])
    recorder = CollectorPostRecorder({"info": "snoozed"})
    monkeypatch.setattr(node_common, "collector_get", collector.get)
    monkeypatch.setattr(inventory, "collector_post", recorder)

    with pytest.raises(ValueError, match="requires exactly one node selector"):
        await inventory.snooze_node_notifications(duration="1h", **kwargs)

    assert collector.calls == []
    assert recorder.calls == []


async def test_create_node_prechecks_nodename_then_posts_payload(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory([{"meta": {"total": 0}, "data": []}])
    recorder = CollectorPostRecorder({"info": "node submitted"})
    monkeypatch.setattr(node_common, "collector_get", collector.get)
    monkeypatch.setattr(inventory, "collector_post", recorder)

    response = await inventory.create_node(
        " node/a ",
        {
            " loc_city ": "Lab City",
            "team_responsible": "Lab Team",
        },
    )

    assert response["nodename"] == "node/a"
    assert response["submitted_properties"] == {
        "loc_city": "Lab City",
        "team_responsible": "Lab Team",
        "nodename": "node/a",
    }
    assert response["collector_response"] == {"info": "node submitted"}
    precheck_call = collector.calls[0]
    assert precheck_call.path == "/nodes"
    assert precheck_call.single_param("props") == "node_id,nodename,app,updated"
    assert precheck_call.single_param("limit") == 2
    assert precheck_call.param_values("filters") == ["nodename=node/a"]
    assert recorder.calls == [
        {
            "path": "/nodes",
            "data": {
                "loc_city": "Lab City",
                "team_responsible": "Lab Team",
                "nodename": "node/a",
            },
            "params": None,
        }
    ]


async def test_create_node_lets_collector_validate_non_delete_errors(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory([{"meta": {"total": 0}, "data": []}])
    recorder = CollectorPostRecorder({"info": "node submitted"})
    monkeypatch.setattr(node_common, "collector_get", collector.get)
    monkeypatch.setattr(inventory, "collector_post", recorder)

    response = await inventory.create_node("node-a", {"node_env": "PPR"})

    assert response["submitted_properties"] == {"node_env": "PPR", "nodename": "node-a"}
    assert recorder.calls == [
        {
            "path": "/nodes",
            "data": {"node_env": "PPR", "nodename": "node-a"},
            "params": None,
        }
    ]


async def test_create_node_rejects_existing_nodename_before_post(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [
            {
                "meta": {"total": 1},
                "data": [
                    {
                        "node_id": "existing-node-id",
                        "nodename": "node-a",
                    }
                ],
            }
        ]
    )
    recorder = CollectorPostRecorder({"info": "node submitted"})
    monkeypatch.setattr(node_common, "collector_get", collector.get)
    monkeypatch.setattr(inventory, "collector_post", recorder)

    with pytest.raises(ValueError, match="node nodename already exists: node-a"):
        await inventory.create_node("node-a", {"role": "test-role"})

    assert collector.calls[0].path == "/nodes"
    assert collector.calls[0].param_values("filters") == ["nodename=node-a"]
    assert recorder.calls == []


@pytest.mark.parametrize("reserved", ["node_id", "nodename"])
async def test_create_node_rejects_reserved_properties_before_post(
    monkeypatch,
    collector_mock_factory,
    reserved,
):
    collector = collector_mock_factory([{"meta": {"total": 0}, "data": []}])
    recorder = CollectorPostRecorder({"info": "node submitted"})
    monkeypatch.setattr(node_common, "collector_get", collector.get)
    monkeypatch.setattr(inventory, "collector_post", recorder)

    with pytest.raises(
        ValueError,
        match=f"create_node properties must not include reserved fields: {reserved}",
    ):
        await inventory.create_node("node-a", {f" {reserved} ": "reserved-value"})

    assert collector.calls[0].path == "/nodes"
    assert recorder.calls == []


async def test_update_node_properties_posts_allowlisted_fields(monkeypatch):
    recorder = CollectorPostRecorder({"info": "node updated"})
    monkeypatch.setattr(inventory, "collector_post", recorder)

    response = await inventory.update_node_properties(
        " node/a ",
        {
            " loc_city ": "Lab City",
            "team_support": "Lab Support",
        },
    )

    assert response["nodename"] == "node/a"
    assert response["updated_properties"] == {
        "loc_city": "Lab City",
        "team_support": "Lab Support",
    }
    assert response["collector_response"] == {"info": "node updated"}
    assert recorder.calls == [
        {
            "path": "/nodes/node%2Fa",
            "data": {"loc_city": "Lab City", "team_support": "Lab Support"},
            "params": None,
        }
    ]


async def test_update_node_properties_resolves_node_id_then_posts_to_nodename(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [
            {
                "meta": {},
                "data": [
                    {
                        "node_id": "node/id",
                        "nodename": "node-a",
                        "status": "up",
                    }
                ],
            }
        ]
    )
    recorder = CollectorPostRecorder({"info": "node updated"})
    monkeypatch.setattr(node_common, "collector_get", collector.get)
    monkeypatch.setattr(inventory, "collector_post", recorder)

    response = await inventory.update_node_properties(
        node_id=" node/id ",
        confirm_node_id="node/id",
        confirm_nodename=" node-a ",
        properties={" loc_city ": "Lab City"},
    )

    assert response["nodename"] == "node-a"
    assert response["updated_properties"] == {"loc_city": "Lab City"}
    assert response["meta"]["selector"] == "node_id"
    assert response["meta"]["resolved_node_id"] == "node/id"
    assert (
        collector.calls[0].single_param("props")
        == inventory.DEFAULT_NODE_UPDATE_SNAPSHOT_PROPS
    )
    assert recorder.calls == [
        {
            "path": "/nodes/node-a",
            "data": {"loc_city": "Lab City"},
            "params": None,
        }
    ]


async def test_update_node_properties_rejects_confirmation_id_mismatch_before_lookup(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory([])
    recorder = CollectorPostRecorder({"info": "node updated"})
    monkeypatch.setattr(node_common, "collector_get", collector.get)
    monkeypatch.setattr(inventory, "collector_post", recorder)

    with pytest.raises(ValueError, match="confirm_node_id must match node_id"):
        await inventory.update_node_properties(
            node_id="node-a-id",
            confirm_node_id="other-node-id",
            confirm_nodename="node-a",
            properties={"loc_city": "Lab City"},
        )

    assert collector.calls == []
    assert recorder.calls == []


async def test_update_node_properties_rejects_empty_payload(monkeypatch):
    recorder = CollectorPostRecorder({"info": "node updated"})
    monkeypatch.setattr(inventory, "collector_post", recorder)

    with pytest.raises(ValueError, match="properties must not be empty"):
        await inventory.update_node_properties("node-a", {})

    assert recorder.calls == []


async def test_update_node_properties_accepts_writable_nodename(monkeypatch):
    recorder = CollectorPostRecorder({"info": "node updated"})
    monkeypatch.setattr(inventory, "collector_post", recorder)

    response = await inventory.update_node_properties("node-a", {"nodename": "node-b"})

    assert response["updated_properties"] == {"nodename": "node-b"}
    assert recorder.calls == [
        {"path": "/nodes/node-a", "data": {"nodename": "node-b"}, "params": None}
    ]


async def test_update_node_properties_rejects_readonly_fields(monkeypatch):
    recorder = CollectorPostRecorder({"info": "node updated"})
    monkeypatch.setattr(inventory, "collector_post", recorder)

    with pytest.raises(ValueError, match="unsupported node writable properties: node_env"):
        await inventory.update_node_properties("node-a", {"node_env": "PPR"})

    assert recorder.calls == []


async def test_list_nodes_builds_collection_params(monkeypatch, collector_mock_factory):
    collector = collector_mock_factory([{"meta": {"total": 1}, "data": [{"nodename": "node-a"}]}])
    monkeypatch.setattr(inventory, "collector_get", collector.get)

    response = await inventory.list_nodes(
        filters={"status": "up"},
        props="nodename,status",
        orderby="nodename",
        search="node-a",
        limit=5,
        offset=10,
    )

    assert response["meta"]["total"] == 1
    call = collector.calls[0]
    assert call.path == "/nodes"
    assert call.single_param("limit") == 5
    assert call.single_param("offset") == 10
    assert call.single_param("props") == "nodename,status"
    assert call.single_param("orderby") == "nodename"
    assert call.single_param("search") == "node-a"
    assert call.param_values("filters") == ["status=up"]


async def test_count_nodes_uses_lightweight_total_query(monkeypatch, collector_mock_factory):
    collector = collector_mock_factory([{"meta": {"total": 42}, "data": [{"nodename": "node-a"}]}])
    monkeypatch.setattr(inventory, "collector_get", collector.get)

    response = await inventory.count_nodes(status="up", app="APP-CODE")

    assert response == {"count": 42, "filters": {"status": "up", "app": "APP-CODE"}}
    call = collector.calls[0]
    assert call.path == "/nodes"
    assert call.single_param("limit") == 1
    assert call.single_param("offset") == 0
    assert call.single_param("props") == "nodename"
    assert call.param_values("orderby") == []
    assert call.param_values("filters") == ["status=up", "app=APP-CODE"]


async def test_get_node_disks_does_not_send_default_orderby(monkeypatch, collector_mock_factory):
    collector = collector_mock_factory([{"meta": {"total": 2}, "data": [{"disk_id": "DISK-ID"}]}])
    monkeypatch.setattr(storage, "collector_get", collector.get)

    response = await storage.get_node_disks(
        "node-a",
        filters={"disk_local": "false"},
        props="disk_id,disk_size",
        limit=2,
    )

    assert response["nodename"] == "node-a"
    assert response["data"] == [{"disk_id": "DISK-ID"}]
    call = collector.calls[0]
    assert call.path == "/nodes/node-a/disks"
    assert call.single_param("limit") == 2
    assert call.single_param("offset") == 0
    assert call.single_param("props") == "svcdisks.disk_id:disk_id,svcdisks.disk_size:disk_size"
    assert call.param_values("orderby") == []
    assert call.param_values("filters") == ["disk_local=false"]


async def test_get_node_disks_uses_qualified_default_props(monkeypatch, collector_mock_factory):
    collector = collector_mock_factory([{"meta": {"total": 1}, "data": [{"disk_id": "DISK-ID"}]}])
    monkeypatch.setattr(storage, "collector_get", collector.get)

    response = await storage.get_node_disks("node-a")

    assert response["data"] == [{"disk_id": "DISK-ID"}]
    props = collector.calls[0].single_param("props")
    assert "svcdisks.disk_size:disk_size" in props
    assert "diskinfo.disk_name:disk_name" in props
    assert "disk_size,disk_used" not in props


async def test_node_disks_response_accepts_collector_numeric_fields():
    response = NodeDisksResponse.model_validate(
        {
            "nodename": "node-a",
            "meta": {},
            "data": [{"app_id": 1, "disk_level": 0, "disk_id": "DISK-ID"}],
        }
    )

    assert response.data[0].app_id == 1
    assert response.data[0].disk_level == 0


async def test_get_node_services_filters_services_instances_by_nodename(monkeypatch, collector_mock_factory):
    collector = collector_mock_factory([{"meta": {"total": 1}, "data": [{"svcname": "svc-a"}]}])
    monkeypatch.setattr(services, "collector_get", collector.get)

    response = await services.get_node_services(
        "node-a",
        filters={"services.svc_status": "up"},
        props="services.svcname:svcname,nodes.nodename:nodename",
        limit=3,
        offset=1,
    )

    assert response["nodename"] == "node-a"
    assert response["meta"]["filter"] == {
        "nodes.nodename": "node-a",
        "services.svc_status": "up",
    }
    call = collector.calls[0]
    assert call.path == "/services_instances"
    assert call.single_param("limit") == 3
    assert call.single_param("offset") == 1
    assert call.param_values("filters") == [
        "nodes.nodename=node-a",
        "services.svc_status=up",
    ]

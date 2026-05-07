import pytest

from opensvc_collector_mcp.core.nodes import inventory, services, storage


@pytest.mark.parametrize("raw, expected", [(" node-a ", "/nodes/node-a"), ("node/a", "/nodes/node%2Fa")])
async def test_get_node_uses_node_detail_endpoint(monkeypatch, collector_mock_factory, raw, expected):
    collector = collector_mock_factory([{"meta": {}, "data": [{"nodename": "node-a"}]}])
    monkeypatch.setattr(inventory, "collector_get", collector.get)

    response = await inventory.get_node(raw)

    assert response["data"] == [{"nodename": "node-a"}]
    assert collector.calls[0].path == expected
    assert collector.calls[0].params is None


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
    assert call.single_param("props") == "disk_id,disk_size"
    assert call.param_values("orderby") == []
    assert call.param_values("filters") == ["disk_local=false"]


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

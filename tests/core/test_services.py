from opensvc_collector_mcp.core.services import inventory, storage


async def test_get_service_uses_service_detail_endpoint(monkeypatch, collector_mock_factory):
    collector = collector_mock_factory([{"meta": {}, "data": [{"svcname": "svc-a"}]}])
    monkeypatch.setattr(inventory, "collector_get", collector.get)

    response = await inventory.get_service(" svc/a ")

    assert response["data"] == [{"svcname": "svc-a"}]
    assert collector.calls[0].path == "/services/svc%2Fa"
    assert collector.calls[0].params is None


async def test_list_services_builds_collection_params(monkeypatch, collector_mock_factory):
    collector = collector_mock_factory([{"meta": {"total": 1}, "data": [{"svcname": "svc-a"}]}])
    monkeypatch.setattr(inventory, "collector_get", collector.get)

    response = await inventory.list_services(
        filters={"svc_status": "up"},
        props="svcname,svc_status",
        orderby="svcname",
        search="svc-a",
        limit=5,
        offset=10,
    )

    assert response["meta"]["total"] == 1
    call = collector.calls[0]
    assert call.path == "/services"
    assert call.single_param("limit") == 5
    assert call.single_param("offset") == 10
    assert call.single_param("props") == "svcname,svc_status"
    assert call.single_param("orderby") == "svcname"
    assert call.single_param("search") == "svc-a"
    assert call.param_values("filters") == ["svc_status=up"]


async def test_count_services_uses_lightweight_total_query(monkeypatch, collector_mock_factory):
    collector = collector_mock_factory([{"meta": {"total": 7}, "data": [{"svcname": "svc-a"}]}])
    monkeypatch.setattr(inventory, "collector_get", collector.get)

    response = await inventory.count_services(svc_app="APP-CODE", svc_status="up")

    assert response == {"count": 7, "filters": {"svc_app": "APP-CODE", "svc_status": "up"}}
    call = collector.calls[0]
    assert call.path == "/services"
    assert call.single_param("limit") == 1
    assert call.single_param("offset") == 0
    assert call.single_param("props") == "svcname"
    assert call.param_values("orderby") == []
    assert call.param_values("filters") == ["svc_app=APP-CODE", "svc_status=up"]


async def test_get_service_nodes_uses_service_nodes_endpoint(monkeypatch, collector_mock_factory):
    collector = collector_mock_factory([{"meta": {"total": 2}, "data": [{"nodename": "node-a"}]}])
    monkeypatch.setattr(inventory, "collector_get", collector.get)

    response = await inventory.get_service_nodes(
        "svc-a",
        filters={"nodes.status": "up"},
        props="nodes.nodename:nodename",
        limit=2,
    )

    assert response["svcname"] == "svc-a"
    assert response["data"] == [{"nodename": "node-a"}]
    assert response["meta"]["node_count"] == 1
    call = collector.calls[0]
    assert call.path == "/services/svc-a/nodes"
    assert call.single_param("limit") == 2
    assert call.single_param("offset") == 0
    assert call.single_param("props") == "nodes.nodename:nodename"
    assert call.param_values("filters") == ["nodes.status=up"]


async def test_get_service_disks_uses_service_disks_endpoint(monkeypatch, collector_mock_factory):
    collector = collector_mock_factory([{"meta": {"total": 1}, "data": [{"disk_id": "DISK-ID"}]}])
    monkeypatch.setattr(storage, "collector_get", collector.get)

    response = await storage.get_service_disks(
        "svc-a",
        filters={"svcdisks.disk_local": "false"},
        props="svcdisks.disk_id:disk_id,svcdisks.disk_size:disk_size",
        limit=4,
        offset=2,
    )

    assert response["svcname"] == "svc-a"
    assert response["data"] == [{"disk_id": "DISK-ID"}]
    assert response["meta"]["disk_count"] == 1
    call = collector.calls[0]
    assert call.path == "/services/svc-a/disks"
    assert call.single_param("limit") == 4
    assert call.single_param("offset") == 2
    assert call.single_param("props") == "svcdisks.disk_id:disk_id,svcdisks.disk_size:disk_size"
    assert call.param_values("filters") == ["svcdisks.disk_local=false"]

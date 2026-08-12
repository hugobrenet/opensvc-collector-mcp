from opensvc_collector_mcp.core.services import (
    _compliance as compliance_common,
    actions,
    compliance,
    inventory,
    instances,
    status_history,
    storage,
)


async def test_get_service_uses_service_detail_endpoint(monkeypatch, collector_mock_factory):
    collector = collector_mock_factory([{"meta": {}, "data": [{"svcname": "svc-a"}]}])
    monkeypatch.setattr(inventory, "collector_get", collector.get)

    response = await inventory.get_service(" svc/a ")

    assert response["data"] == [{"svcname": "svc-a"}]
    assert collector.calls[0].path == "/services/svc%2Fa"
    assert collector.calls[0].params is None


async def test_list_services_builds_collection_params(monkeypatch, collector_mock_factory):
    collector = collector_mock_factory(
        [
            {
                "pagination": {
                    "limit": 5,
                    "offset": 10,
                    "returned": 1,
                    "next_offset": None,
                    "complete": True,
                },
                "data": [{"svcname": "svc-a"}],
            }
        ]
    )
    monkeypatch.setattr(inventory, "collector_get_page", collector.get)

    response = await inventory.list_services(
        filters={"svc_status": "up"},
        props="svcname,svc_status",
        orderby="svcname",
        search="svc-a",
        limit=5,
        offset=10,
    )

    assert response["pagination"]["complete"] is True
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
    collector = collector_mock_factory(
        [
            {
                "pagination": {
                    "limit": 2,
                    "offset": 0,
                    "returned": 1,
                    "next_offset": None,
                    "complete": True,
                },
                "data": [{"nodename": "node-a"}],
            }
        ]
    )
    monkeypatch.setattr(instances, "collector_get_page", collector.get)

    response = await instances.get_service_nodes(
        "svc-a",
        filters={"nodes.status": "up"},
        props="nodes.nodename:nodename",
        limit=2,
    )

    assert response["svcname"] == "svc-a"
    assert response["data"] == [{"nodename": "node-a"}]
    assert response["pagination"]["complete"] is True
    call = collector.calls[0]
    assert call.path == "/services/svc-a/nodes"
    assert call.single_param("limit") == 2
    assert call.single_param("offset") == 0
    assert call.single_param("props") == "nodes.nodename:nodename"
    assert call.param_values("filters") == ["nodes.status=up"]


async def test_get_service_disks_uses_service_disks_endpoint(monkeypatch, collector_mock_factory):
    collector = collector_mock_factory(
        [
            {
                "pagination": {
                    "limit": 4,
                    "offset": 2,
                    "returned": 1,
                    "next_offset": None,
                    "complete": True,
                },
                "data": [{"disk_id": "DISK-ID"}],
            }
        ]
    )
    monkeypatch.setattr(storage, "collector_get_page", collector.get)

    response = await storage.get_service_disks(
        "svc-a",
        filters={"svcdisks.disk_local": "false"},
        props="svcdisks.disk_id:disk_id,svcdisks.disk_size:disk_size",
        limit=4,
        offset=2,
    )

    assert response["svcname"] == "svc-a"
    assert response["data"] == [{"disk_id": "DISK-ID"}]
    assert response["pagination"]["complete"] is True
    call = collector.calls[0]
    assert call.path == "/services/svc-a/disks"
    assert call.single_param("limit") == 4
    assert call.single_param("offset") == 2
    assert call.single_param("props") == "svcdisks.disk_id:disk_id,svcdisks.disk_size:disk_size"
    assert call.param_values("filters") == ["svcdisks.disk_local=false"]


async def test_service_actions_latest_pages_use_logical_offsets(
    monkeypatch,
    collector_mock_factory,
):
    probe = collector_mock_factory([{"meta": {"total": 25}, "data": [{}]}])
    page = collector_mock_factory(
        [
            {
                "pagination": {
                    "limit": 10,
                    "offset": 5,
                    "returned": 10,
                    "next_offset": 15,
                    "complete": False,
                    "truncated": False,
                },
                "data": [{"action": str(index)} for index in range(5, 15)],
            }
        ]
    )
    monkeypatch.setattr(actions, "collector_get", probe.get)
    monkeypatch.setattr(actions, "collector_get_page", page.get)

    response = await actions.get_service_actions(
        "svc-a",
        limit=10,
        offset=10,
        latest=True,
        latest_first=True,
    )

    assert response["pagination"] == {
        "limit": 10,
        "offset": 10,
        "returned": 10,
        "next_offset": 20,
        "complete": False,
        "truncated": False,
    }
    assert response["data"][0]["action"] == "14"
    assert response["data"][-1]["action"] == "5"
    assert "meta" not in response
    assert page.calls[0].single_param("limit") == 10
    assert page.calls[0].single_param("offset") == 5


async def test_service_compliance_status_returns_page_and_page_summary(
    monkeypatch,
    collector_mock_factory,
):
    page = collector_mock_factory(
        [
            {
                "pagination": {
                    "limit": 1,
                    "offset": 2,
                    "returned": 1,
                    "next_offset": 3,
                    "complete": False,
                    "truncated": False,
                },
                "data": [
                    {
                        "node_id": "NODE-ID",
                        "run_module": "module.failed",
                        "run_status": 1,
                    }
                ],
            }
        ]
    )

    async def nodenames(_node_ids):
        return {"NODE-ID": "node-a"}

    monkeypatch.setattr(compliance, "collector_get_page", page.get)
    monkeypatch.setattr(compliance_common, "get_nodenames_by_node_ids", nodenames)

    response = await compliance.get_service_compliance_status(
        "svc-a",
        limit=1,
        offset=2,
    )

    assert response["pagination"]["next_offset"] == 3
    assert response["summary"]["error_count"] == 1
    assert response["summary"]["node_names_resolved"] is True
    assert response["data"][0]["nodename"] == "node-a"
    assert "meta" not in response
    assert page.calls[0].single_param("orderby") == "~run_date"


async def test_service_status_history_uses_direct_pages(
    monkeypatch,
    collector_mock_factory,
):
    async def identity(_svcname):
        return {
            "svc_id": "SERVICE-ID",
            "service": {
                "svc_id": "SERVICE-ID",
                "svcname": "svc-a",
                "svc_availstatus": "up",
            },
        }

    pages = collector_mock_factory(
        [
            {
                "pagination": {
                    "limit": 2,
                    "offset": 2,
                    "returned": 2,
                    "next_offset": 4,
                    "complete": False,
                    "truncated": False,
                },
                "data": [{"id": 3}, {"id": 2}],
            },
            {
                "pagination": {
                    "limit": 1,
                    "offset": 0,
                    "returned": 1,
                    "next_offset": None,
                    "complete": True,
                    "truncated": False,
                },
                "data": [
                    {
                        "id": 4,
                        "svc_availstatus": "up",
                        "svc_begin": "2026-01-01 00:00:00",
                    }
                ],
            },
        ]
    )
    monkeypatch.setattr(status_history, "get_service_identity", identity)
    monkeypatch.setattr(status_history, "collector_get_page", pages.get)

    response = await status_history.get_service_status_history(
        "svc-a",
        limit=2,
        offset=2,
    )

    assert response["pagination"]["next_offset"] == 4
    assert response["current_status_since"] == "2026-01-01 00:00:00"
    assert "meta" not in response
    assert pages.calls[0].single_param("orderby") == "~svc_begin"
    assert pages.calls[0].single_param("offset") == 2
    assert pages.calls[1].single_param("limit") == 1

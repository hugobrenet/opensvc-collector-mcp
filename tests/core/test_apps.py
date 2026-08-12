from opensvc_collector_mcp.core.apps import (
    _relations,
    groups,
    inventory,
    nodes,
    quotas,
    responsibility,
    services,
)


async def test_list_apps_builds_collection_params(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [
            {
                "pagination": {
                    "limit": 5,
                    "offset": 2,
                    "returned": 1,
                    "next_offset": None,
                    "complete": True,
                },
                "data": [{"app": "APP-A"}],
            }
        ]
    )
    monkeypatch.setattr(inventory, "collector_get_page", collector.get)

    response = await inventory.list_apps(
        filters={"app_domain": "DOMAIN-A"},
        props="app,description",
        orderby="app DESC",
        search="APP-A",
        limit=5,
        offset=2,
    )

    assert response["data"] == [{"app": "APP-A"}]
    call = collector.calls[0]
    assert call.path == "/apps"
    assert call.single_param("props") == "app,description"
    assert call.single_param("orderby") == "app DESC"
    assert call.single_param("search") == "APP-A"
    assert call.single_param("limit") == 5
    assert call.single_param("offset") == 2
    assert call.param_values("filters") == ["app_domain=DOMAIN-A"]


async def test_count_apps_uses_lightweight_total_query(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory([{"meta": {"total": 7}, "data": []}])
    monkeypatch.setattr(inventory, "collector_get", collector.get)

    response = await inventory.count_apps(filters={"app_domain": "DOMAIN-A"})

    assert response == {
        "count": 7,
        "filters": {"app_domain": "DOMAIN-A"},
        "search": None,
    }
    call = collector.calls[0]
    assert call.path == "/apps"
    assert call.single_param("props") == "app"
    assert call.single_param("limit") == 1
    assert call.single_param("offset") == 0


async def test_get_app_quotes_selector_and_preserves_detail_meta(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [{"meta": {"total": 1}, "data": [{"app": "APP/A"}]}]
    )
    monkeypatch.setattr(inventory, "collector_get", collector.get)

    response = await inventory.get_app(" APP/A ", props="app,description")

    assert collector.calls[0].path == "/apps/APP%2FA"
    assert collector.calls[0].params == {"props": "app,description"}
    assert response["meta"]["selector"] == "APP/A"
    assert response["meta"]["source"] == "app_detail"
    assert response["meta"]["count"] == 1


async def test_am_i_responsible_for_app_uses_scoped_endpoint(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory([{"data": [{"role": "OPS"}]}])
    monkeypatch.setattr(responsibility, "collector_get", collector.get)

    response = await responsibility.am_i_responsible_for_app(" APP/A ")

    assert collector.calls[0].path == "/apps/APP%2FA/am_i_responsible"
    assert response["app"] == "APP/A"
    assert response["responsible"] is True


async def test_app_nodes_page_and_count_share_relation_contract(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [
            {"pagination": {}, "data": [{"nodename": "node-a"}]},
            {"meta": {"total": 3}, "data": []},
        ]
    )
    monkeypatch.setattr(_relations, "collector_get_page", collector.get)
    monkeypatch.setattr(_relations, "collector_get", collector.get)

    page = await nodes.get_app_nodes(
        "APP/A",
        filters={"status": "up"},
        props="nodename,status",
    )
    count = await nodes.count_app_nodes("APP/A")

    assert page["app"] == "APP/A"
    assert count["count"] == 3
    assert collector.calls[0].path == "/apps/APP%2FA/nodes"
    assert collector.calls[0].param_values("filters") == ["status=up"]
    assert collector.calls[1].path == "/apps/APP%2FA/nodes"
    assert collector.calls[1].params == {
        "props": "nodename",
        "limit": 1,
        "offset": 0,
    }


async def test_app_services_use_service_default_props(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [{"pagination": {}, "data": [{"svcname": "svc-a"}]}]
    )
    monkeypatch.setattr(_relations, "collector_get_page", collector.get)

    response = await services.get_app_services("APP-A")

    assert response["app"] == "APP-A"
    assert collector.calls[0].path == "/apps/APP-A/services"
    assert collector.calls[0].single_param("props") == (
        "svcname,svc_app,svc_env,svc_status,svc_availstatus,svc_topology,"
        "svc_nodes,svc_drpnodes,svc_frozen,svc_ha,svc_created,updated"
    )


async def test_app_group_relations_use_their_scoped_paths(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [
            {"pagination": {}, "data": [{"role": "OPS"}]},
            {"pagination": {}, "data": [{"role": "PUB"}]},
        ]
    )
    monkeypatch.setattr(_relations, "collector_get_page", collector.get)

    responsibles = await groups.get_app_responsibles("APP-A")
    publications = await groups.get_app_publications("APP-A")

    assert responsibles["app"] == "APP-A"
    assert publications["app"] == "APP-A"
    assert collector.calls[0].path == "/apps/APP-A/responsibles"
    assert collector.calls[1].path == "/apps/APP-A/publications"
    assert collector.calls[0].single_param("props") == (
        "id,role,privilege,description"
    )


async def test_app_quotas_use_quota_relation_defaults(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [{"pagination": {}, "data": [{"array_name": "array-a"}]}]
    )
    monkeypatch.setattr(_relations, "collector_get_page", collector.get)

    response = await quotas.get_app_quotas("APP-A")

    assert response["app"] == "APP-A"
    assert collector.calls[0].path == "/apps/APP-A/quotas"
    assert collector.calls[0].single_param("props") == (
        "app,array_name,array_model,dg_name,quota,quota_used,"
        "dg_size,dg_used,dg_free,dg_reserved,dg_reservable"
    )

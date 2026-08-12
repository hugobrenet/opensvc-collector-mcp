from opensvc_collector_mcp.core.arrays import (
    diskgroups,
    inventory,
    quotas,
    relations,
)


async def test_list_arrays_builds_collection_params(
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
                "data": [{"array_name": "array-a"}],
            }
        ]
    )
    monkeypatch.setattr(inventory, "collector_get_page", collector.get)

    response = await inventory.list_arrays(
        filters={"array_model": "model-a"},
        props="id,array_name",
        orderby="array_name DESC",
        search="array-a",
        limit=5,
        offset=2,
    )

    assert response["data"] == [{"array_name": "array-a"}]
    call = collector.calls[0]
    assert call.path == "/arrays"
    assert call.single_param("props") == "id,array_name"
    assert call.single_param("orderby") == "array_name DESC"
    assert call.single_param("search") == "array-a"
    assert call.single_param("limit") == 5
    assert call.single_param("offset") == 2
    assert call.param_values("filters") == ["array_model=model-a"]


async def test_count_arrays_uses_lightweight_total_query(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory([{"meta": {"total": 4}, "data": []}])
    monkeypatch.setattr(inventory, "collector_get", collector.get)

    response = await inventory.count_arrays(filters={"array_model": "model-a"})

    assert response == {
        "count": 4,
        "filters": {"array_model": "model-a"},
        "search": None,
    }
    call = collector.calls[0]
    assert call.path == "/arrays"
    assert call.single_param("props") == "array_name"
    assert call.single_param("limit") == 1
    assert call.single_param("offset") == 0


async def test_get_array_quotes_selector_and_preserves_detail_meta(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [{"meta": {"total": 1}, "data": [{"array_name": "array/a"}]}]
    )
    monkeypatch.setattr(inventory, "collector_get", collector.get)

    response = await inventory.get_array(" array/a ", props="id,array_name")

    assert collector.calls[0].path == "/arrays/array%2Fa"
    assert collector.calls[0].params == {"props": "id,array_name"}
    assert response["meta"]["selector"] == "array/a"
    assert response["meta"]["source"] == "array_detail"
    assert response["meta"]["count"] == 1


async def test_get_array_diskgroups_builds_scoped_page(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [
            {
                "pagination": {
                    "limit": 10,
                    "offset": 0,
                    "returned": 1,
                    "next_offset": None,
                    "complete": True,
                },
                "data": [{"dg_name": "dg-a"}],
            }
        ]
    )
    monkeypatch.setattr(diskgroups, "collector_get_page", collector.get)

    response = await diskgroups.get_array_diskgroups(
        "array/a",
        filters={"dg_name": "dg-a"},
        props="id,dg_name",
        limit=10,
    )

    assert response["array"] == "array/a"
    assert collector.calls[0].path == "/arrays/array%2Fa/diskgroups"
    assert collector.calls[0].single_param("props") == "id,dg_name"
    assert collector.calls[0].param_values("filters") == ["dg_name=dg-a"]


async def test_get_array_diskgroup_quota_builds_nested_detail_path(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [{"meta": {}, "data": [{"id": 9, "quota": 100}]}]
    )
    monkeypatch.setattr(quotas, "collector_get", collector.get)

    response = await quotas.get_array_diskgroup_quota(
        "array/a",
        "dg/a",
        "quota/a",
        props="id,quota",
    )

    assert collector.calls[0].path == (
        "/arrays/array%2Fa/diskgroups/dg%2Fa/quotas/quota%2Fa"
    )
    assert collector.calls[0].params == {"props": "id,quota"}
    assert response["array"] == "array/a"
    assert response["diskgroup"] == "dg/a"
    assert response["quota"] == "quota/a"
    assert response["meta"]["count"] == 1


async def test_array_proxy_and_target_relations_use_their_default_props(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [
            {"pagination": {}, "data": [{"node_id": 1}]},
            {"pagination": {}, "data": [{"array_tgtid": "target-a"}]},
        ]
    )
    monkeypatch.setattr(relations, "collector_get_page", collector.get)

    proxies = await relations.get_array_proxies("array-a")
    targets = await relations.get_array_targets("array-a")

    assert proxies["array"] == "array-a"
    assert targets["array"] == "array-a"
    assert collector.calls[0].path == "/arrays/array-a/proxies"
    assert collector.calls[0].single_param("props") == "id,array_id,node_id"
    assert collector.calls[1].path == "/arrays/array-a/targets"
    assert collector.calls[1].single_param("props") == "id,array_id,array_tgtid"

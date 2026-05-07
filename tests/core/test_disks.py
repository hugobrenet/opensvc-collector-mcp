import httpx

from opensvc_collector_mcp.core.disks import inventory


def not_found_error() -> httpx.HTTPStatusError:
    request = httpx.Request("GET", "https://collector.invalid/disks/DISK-ID")
    response = httpx.Response(404, request=request)
    return httpx.HTTPStatusError("not found", request=request, response=response)


async def test_list_disks_maps_common_filter_aliases(monkeypatch, collector_mock_factory):
    collector = collector_mock_factory([{"meta": {"total": 1}, "data": [{"disk_id": "DISK-ID"}]}])
    monkeypatch.setattr(inventory, "collector_get", collector.get)

    response = await inventory.list_disks(
        filters={"node_id": "NODE-ID", "array_name": "ARRAY-NAME"},
        props="svcdisks.disk_id:disk_id",
        limit=5,
        offset=2,
    )

    assert response["data"] == [{"disk_id": "DISK-ID"}]
    call = collector.calls[0]
    assert call.path == "/disks"
    assert call.single_param("limit") == 5
    assert call.single_param("offset") == 2
    assert call.single_param("props") == "svcdisks.disk_id:disk_id"
    assert call.param_values("filters") == [
        "svcdisks.node_id=NODE-ID",
        "stor_array.array_name=ARRAY-NAME",
    ]


async def test_count_disks_uses_total_and_filter_aliases(monkeypatch, collector_mock_factory):
    collector = collector_mock_factory([{"meta": {"total": 72}, "data": []}])
    monkeypatch.setattr(inventory, "collector_get", collector.get)

    response = await inventory.count_disks(filters={"disk_id": "DISK-ID"})

    assert response == {
        "count": 72,
        "filters": {"diskinfo.disk_id": "DISK-ID"},
        "search": None,
    }
    call = collector.calls[0]
    assert call.path == "/disks"
    assert call.single_param("limit") == 1
    assert call.single_param("offset") == 0
    assert call.param_values("props") == []
    assert call.param_values("filters") == ["diskinfo.disk_id=DISK-ID"]


async def test_get_disk_uses_disk_detail_endpoint(monkeypatch, collector_mock_factory):
    collector = collector_mock_factory([{"meta": {}, "data": [{"disk_id": "DISK-ID"}]}])
    monkeypatch.setattr(inventory, "collector_get", collector.get)

    response = await inventory.get_disk(" DISK-ID ", props="svcdisks.disk_id:disk_id")

    assert response["disk"] == "DISK-ID"
    assert response["meta"]["source"] == "disk_detail"
    assert response["data"] == [{"disk_id": "DISK-ID"}]
    call = collector.calls[0]
    assert call.path == "/disks/DISK-ID"
    assert call.params == {"props": "svcdisks.disk_id:disk_id"}


async def test_get_disk_falls_back_to_filter_when_detail_returns_404(monkeypatch, collector_mock_factory):
    collector = collector_mock_factory([
        not_found_error(),
        {"meta": {"total": 1}, "data": [{"disk_id": "LOCAL-DISK-ID"}]},
    ])
    monkeypatch.setattr(inventory, "collector_get", collector.get)

    response = await inventory.get_disk("LOCAL-DISK-ID", props="svcdisks.disk_id:disk_id")

    assert response["meta"]["source"] == "disk_detail_by_filter"
    assert response["data"] == [{"disk_id": "LOCAL-DISK-ID"}]
    assert collector.calls[0].path == "/disks/LOCAL-DISK-ID"
    fallback = collector.calls[1]
    assert fallback.path == "/disks"
    assert fallback.single_param("limit") == 1000
    assert fallback.single_param("offset") == 0
    assert fallback.single_param("props") == "svcdisks.disk_id:disk_id"
    assert fallback.param_values("filters") == ["diskinfo.disk_id=LOCAL-DISK-ID"]


async def test_list_disk_props_strips_known_table_prefixes(monkeypatch, collector_mock_factory):
    collector = collector_mock_factory([
        {
            "meta": {
                "available_props": [
                    "svcdisks.disk_id",
                    "diskinfo.disk_name",
                    "stor_array.array_name",
                ]
            },
            "data": [],
        }
    ])
    monkeypatch.setattr(inventory, "collector_get", collector.get)

    response = await inventory.list_disk_props()

    assert response["count"] == 3
    assert response["disk_props"] == ["disk_id", "disk_name", "array_name"]
    assert collector.calls[0].path == "/disks"
    assert collector.calls[0].params == {"limit": 1, "offset": 0}

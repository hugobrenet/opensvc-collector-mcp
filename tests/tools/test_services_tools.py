from opensvc_collector_mcp.tools import services as service_tools


class CoreRecorder:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def __call__(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


async def test_list_services_tool_passes_request_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder({"meta": {"total": 1}, "data": [{"svcname": "svc-a"}]})
    monkeypatch.setattr(service_tools, "core_list_services", recorder)

    result = await mcp_client.call_tool(
        "list_services",
        {
            "request": {
                "svc_status": "up",
                "props": "svcname,svc_status",
                "orderby": "svcname",
                "search": "svc-a",
                "limit": 5,
                "offset": 2,
            }
        },
    )

    assert result.structured_content == {"meta": {"total": 1}, "data": [{"svcname": "svc-a"}]}
    assert recorder.calls == [
        {
            "filters": {"svc_status": "up"},
            "props": "svcname,svc_status",
            "orderby": "svcname",
            "search": "svc-a",
            "limit": 5,
            "offset": 2,
        }
    ]


async def test_count_services_tool_passes_merged_filters_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder({"count": 2, "filters": {"svc_status": "up"}})
    monkeypatch.setattr(service_tools, "core_count_services", recorder)

    result = await mcp_client.call_tool(
        "count_services",
        {"request": {"svc_status": "up"}},
    )

    assert result.structured_content == {"count": 2, "filters": {"svc_status": "up"}}
    assert recorder.calls == [{"filters": {"svc_status": "up"}}]


async def test_get_service_tool_passes_svcname_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder({"meta": {}, "data": [{"svcname": "svc-a"}]})
    monkeypatch.setattr(service_tools, "core_get_service", recorder)

    result = await mcp_client.call_tool(
        "get_service",
        {"request": {"svcname": "svc-a"}},
    )

    assert result.structured_content == {"meta": {}, "data": [{"svcname": "svc-a"}]}
    assert recorder.calls == [{"svcname": "svc-a"}]


async def test_get_service_nodes_tool_passes_relation_request_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder(
        {"svcname": "svc-a", "meta": {"total": 1}, "data": [{"nodename": "node-a"}]}
    )
    monkeypatch.setattr(service_tools, "core_get_service_nodes", recorder)

    result = await mcp_client.call_tool(
        "get_service_nodes",
        {
            "request": {
                "svcname": "svc-a",
                "filters": {"nodes.status": "up"},
                "props": "nodes.nodename:nodename",
                "limit": 3,
            }
        },
    )

    assert result.structured_content["data"] == [{"nodename": "node-a"}]
    assert recorder.calls == [
        {
            "svcname": "svc-a",
            "filters": {"nodes.status": "up"},
            "props": "nodes.nodename:nodename",
            "orderby": None,
            "search": None,
            "limit": 3,
            "offset": 0,
        }
    ]


async def test_get_service_disks_tool_passes_relation_request_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder(
        {"svcname": "svc-a", "meta": {"total": 1}, "data": [{"disk_id": "DISK-ID"}]}
    )
    monkeypatch.setattr(service_tools, "core_get_service_disks", recorder)

    result = await mcp_client.call_tool(
        "get_service_disks",
        {
            "request": {
                "svcname": "svc-a",
                "filters": {"svcdisks.disk_local": "false"},
                "props": "svcdisks.disk_id:disk_id",
                "limit": 4,
                "offset": 1,
            }
        },
    )

    assert result.structured_content["data"] == [{"disk_id": "DISK-ID"}]
    assert recorder.calls == [
        {
            "svcname": "svc-a",
            "filters": {"svcdisks.disk_local": "false"},
            "props": "svcdisks.disk_id:disk_id",
            "orderby": None,
            "search": None,
            "limit": 4,
            "offset": 1,
        }
    ]

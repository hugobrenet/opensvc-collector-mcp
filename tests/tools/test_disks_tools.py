from opensvc_collector_mcp.tools import disks as disk_tools


class CoreRecorder:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def __call__(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


async def test_list_disks_tool_passes_request_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder({"meta": {"total": 1}, "data": [{"disk_id": "DISK-ID"}]})
    monkeypatch.setattr(disk_tools, "core_list_disks", recorder)

    result = await mcp_client.call_tool(
        "list_disks",
        {
            "request": {
                "node_id": "NODE-ID",
                "array_name": "ARRAY-NAME",
                "props": "svcdisks.disk_id:disk_id",
                "limit": 5,
                "offset": 2,
            }
        },
    )

    assert result.structured_content["data"][0]["disk_id"] == "DISK-ID"
    assert recorder.calls == [
        {
            "filters": {"node_id": "NODE-ID", "array_name": "ARRAY-NAME"},
            "props": "svcdisks.disk_id:disk_id",
            "orderby": None,
            "search": None,
            "limit": 5,
            "offset": 2,
        }
    ]


async def test_count_disks_tool_passes_filters_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder({"count": 2, "filters": {"node_id": "NODE-ID"}, "search": None})
    monkeypatch.setattr(disk_tools, "core_count_disks", recorder)

    result = await mcp_client.call_tool(
        "count_disks",
        {"request": {"node_id": "NODE-ID"}},
    )

    assert result.structured_content == {
        "count": 2,
        "filters": {"node_id": "NODE-ID"},
        "search": None,
    }
    assert recorder.calls == [{"filters": {"node_id": "NODE-ID"}, "search": None}]


async def test_get_disk_tool_passes_disk_selector_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder(
        {"disk": "DISK-ID", "meta": {"source": "disk_detail"}, "data": [{"disk_id": "DISK-ID"}]}
    )
    monkeypatch.setattr(disk_tools, "core_get_disk", recorder)

    result = await mcp_client.call_tool(
        "get_disk",
        {"request": {"disk": "DISK-ID", "props": "svcdisks.disk_id:disk_id"}},
    )

    assert result.structured_content["disk"] == "DISK-ID"
    assert result.structured_content["data"][0]["disk_id"] == "DISK-ID"
    assert recorder.calls == [{"disk": "DISK-ID", "props": "svcdisks.disk_id:disk_id"}]


async def test_list_disk_props_tool_calls_core(monkeypatch, mcp_client):
    recorder = CoreRecorder(
        {
            "count": 1,
            "available_props": ["svcdisks.disk_id"],
            "disk_props": ["disk_id"],
        }
    )
    monkeypatch.setattr(disk_tools, "core_list_disk_props", recorder)

    result = await mcp_client.call_tool("list_disk_props", {})

    assert result.structured_content == {
        "count": 1,
        "available_props": ["svcdisks.disk_id"],
        "disk_props": ["disk_id"],
    }
    assert recorder.calls == [{}]

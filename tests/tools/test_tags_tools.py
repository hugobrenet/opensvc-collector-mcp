from opensvc_collector_mcp.tools import tags as tag_tools


class CoreRecorder:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def __call__(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


async def test_create_tag_tool_passes_request_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder(
        {
            "meta": {"count": 1},
            "data": [
                {
                    "tag_id": "tag-1",
                    "tag_name": "mcp-test-tag",
                    "tag_data": "created by test",
                }
            ],
        }
    )
    monkeypatch.setattr(tag_tools, "core_create_tag", recorder)

    result = await mcp_client.call_tool(
        "create_tag",
        {
            "request": {
                "tag_name": "mcp-test-tag",
                "tag_data": "created by test",
            }
        },
    )

    assert result.structured_content["data"][0]["tag_name"] == "mcp-test-tag"
    assert recorder.calls == [
        {
            "tag_name": "mcp-test-tag",
            "tag_data": "created by test",
            "tag_exclude": None,
        }
    ]

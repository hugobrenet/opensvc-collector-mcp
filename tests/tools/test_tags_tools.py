from opensvc_collector_mcp.tools import tags as tag_tools


class CoreRecorder:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def __call__(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


async def test_delete_tag_tool_passes_request_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder(
        {
            "tag_id": "tag-1",
            "tag_name": "mcp-test-tag",
            "tag": {"tag_id": "tag-1", "tag_name": "mcp-test-tag"},
            "deleted": True,
            "collector_response": {"meta": {"count": 1}, "data": []},
            "meta": {"source": "tags/<tag_id>"},
        }
    )
    monkeypatch.setattr(tag_tools, "core_delete_tag", recorder)

    result = await mcp_client.call_tool(
        "delete_tag",
        {
            "request": {
                "tag_name": "mcp-test-tag",
                "confirm_tag_name": "mcp-test-tag",
            }
        },
    )

    assert result.structured_content["deleted"] is True
    assert result.structured_content["tag_name"] == "mcp-test-tag"
    assert recorder.calls == [
        {
            "tag_id": None,
            "tag_name": "mcp-test-tag",
            "confirm_tag_name": "mcp-test-tag",
        }
    ]


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
            "info": "tag 'mcp-test-tag' created",
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
    assert result.structured_content["info"] == "tag 'mcp-test-tag' created"
    assert recorder.calls == [
        {
            "tag_name": "mcp-test-tag",
            "tag_data": "created by test",
            "tag_exclude": None,
        }
    ]

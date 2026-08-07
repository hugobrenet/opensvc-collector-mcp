import pytest
from fastmcp.exceptions import ToolError

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
                "tag_id": "tag-1",
            }
        },
    )

    assert result.structured_content["deleted"] is True
    assert result.structured_content["tag_name"] == "mcp-test-tag"
    assert recorder.calls == [
        {
            "tag_id": "tag-1",
            "tag_name": None,
        }
    ]


async def test_delete_tag_tool_rejects_tag_name_selector(monkeypatch, mcp_client):
    recorder = CoreRecorder({})
    monkeypatch.setattr(tag_tools, "core_delete_tag", recorder)

    with pytest.raises(ToolError) as exc_info:
        await mcp_client.call_tool(
            "delete_tag",
            {
                "request": {
                    "tag_name": "mcp-test-tag",
                }
            }
        )

    assert '"loc": ["request", "tag_id"]' in str(exc_info.value)
    assert '"loc": ["request", "tag_name"]' in str(exc_info.value)
    assert recorder.calls == []


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

async def test_attach_tag_to_node_tool_passes_request_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder(
        {
            "tag_id": "tag-1",
            "tag_name": "mcp-test-tag",
            "tag": {"tag_id": "tag-1", "tag_name": "mcp-test-tag"},
            "node_id": "node-1",
            "nodename": "lab-node-01",
            "node": {"node_id": "node-1", "nodename": "lab-node-01"},
            "attached": True,
            "tag_attach_data": "scope=lab",
            "collector_response": {"info": "tag attached"},
            "meta": {"source": "tags/<tag_id>/nodes/<node_id>"},
        }
    )
    monkeypatch.setattr(tag_tools, "core_attach_tag_to_node", recorder)

    result = await mcp_client.call_tool(
        "attach_tag_to_node",
        {
            "request": {
                "tag_id": "tag-1",
                "node_id": "node-1",
                "nodename": "lab-node-01",
                "tag_attach_data": "scope=lab",
            }
        },
    )

    assert result.structured_content["attached"] is True
    assert result.structured_content["node_id"] == "node-1"
    assert recorder.calls == [
        {
            "tag_id": "tag-1",
            "tag_name": None,
            "node_id": "node-1",
            "nodename": "lab-node-01",
            "tag_attach_data": "scope=lab",
        }
    ]


async def test_attach_tag_to_service_tool_passes_request_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder(
        {
            "tag_id": "tag-1",
            "tag_name": "mcp-test-tag",
            "tag": {"tag_id": "tag-1", "tag_name": "mcp-test-tag"},
            "svc_id": "svc-1",
            "svcname": "svc/app/test",
            "service": {"svc_id": "svc-1", "svcname": "svc/app/test"},
            "attached": True,
            "collector_response": {"info": "tag attached"},
            "meta": {"source": "tags/<tag_id>/services/<svc_id>"},
        }
    )
    monkeypatch.setattr(tag_tools, "core_attach_tag_to_service", recorder)

    result = await mcp_client.call_tool(
        "attach_tag_to_service",
        {
            "request": {
                "tag_id": "tag-1",
                "svc_id": "svc-1",
                "svcname": "svc/app/test",
            }
        },
    )

    assert result.structured_content["attached"] is True
    assert result.structured_content["svc_id"] == "svc-1"
    assert recorder.calls == [
        {
            "tag_id": "tag-1",
            "tag_name": None,
            "svc_id": "svc-1",
            "svcname": "svc/app/test",
        }
    ]


async def test_detach_tag_from_service_tool_passes_request_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder(
        {
            "tag_id": "tag-1",
            "tag_name": "mcp-test-tag",
            "tag": {"tag_id": "tag-1", "tag_name": "mcp-test-tag"},
            "svc_id": "svc-1",
            "svcname": "svc/app/test",
            "service": {"svc_id": "svc-1", "svcname": "svc/app/test"},
            "relation": {"svc_id": "svc-1", "svcname": "svc/app/test"},
            "detached": True,
            "collector_response": {"info": "tag detached"},
            "meta": {"source": "tags/<tag_id>/services/<svc_id>"},
        }
    )
    monkeypatch.setattr(tag_tools, "core_detach_tag_from_service", recorder)

    result = await mcp_client.call_tool(
        "detach_tag_from_service",
        {
            "request": {
                "tag_id": "tag-1",
                "svc_id": "svc-1",
                "svcname": "svc/app/test",
            }
        },
    )

    assert result.structured_content["detached"] is True
    assert result.structured_content["svc_id"] == "svc-1"
    assert recorder.calls == [
        {
            "tag_id": "tag-1",
            "tag_name": None,
            "svc_id": "svc-1",
            "svcname": "svc/app/test",
        }
    ]


async def test_detach_tag_from_node_tool_passes_request_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder(
        {
            "tag_id": "tag-1",
            "tag_name": "mcp-test-tag",
            "tag": {"tag_id": "tag-1", "tag_name": "mcp-test-tag"},
            "node_id": "node-1",
            "nodename": "lab-node-01",
            "node": {"node_id": "node-1", "nodename": "lab-node-01"},
            "relation": {"node_id": "node-1", "nodename": "lab-node-01"},
            "detached": True,
            "collector_response": {"info": "tag detached"},
            "meta": {"source": "tags/<tag_id>/nodes/<node_id>"},
        }
    )
    monkeypatch.setattr(tag_tools, "core_detach_tag_from_node", recorder)

    result = await mcp_client.call_tool(
        "detach_tag_from_node",
        {
            "request": {
                "tag_id": "tag-1",
                "node_id": "node-1",
                "nodename": "lab-node-01",
            }
        },
    )

    assert result.structured_content["detached"] is True
    assert result.structured_content["node_id"] == "node-1"
    assert recorder.calls == [
        {
            "tag_id": "tag-1",
            "tag_name": None,
            "node_id": "node-1",
            "nodename": "lab-node-01",
        }
    ]


@pytest.mark.parametrize(
    ("tool_name", "core_attr", "target_fields"),
    [
        ("attach_tag_to_node", "core_attach_tag_to_node", {"node_id": "node-1", "nodename": "lab-node-01"}),
        ("attach_tag_to_service", "core_attach_tag_to_service", {"svc_id": "svc-1", "svcname": "svc/app/test"}),
        ("detach_tag_from_node", "core_detach_tag_from_node", {"node_id": "node-1", "nodename": "lab-node-01"}),
        ("detach_tag_from_service", "core_detach_tag_from_service", {"svc_id": "svc-1", "svcname": "svc/app/test"}),
    ],
)
async def test_tag_relation_tools_reject_tag_name_selector(
    monkeypatch,
    mcp_client,
    tool_name,
    core_attr,
    target_fields,
):
    recorder = CoreRecorder({})
    monkeypatch.setattr(tag_tools, core_attr, recorder)

    with pytest.raises(ToolError) as exc_info:
        await mcp_client.call_tool(
            tool_name,
            {
                "request": {
                    "tag_name": "mcp-test-tag",
                    **target_fields,
                }
            },
        )

    assert '"loc": ["request", "tag_id"]' in str(exc_info.value)
    assert '"loc": ["request", "tag_name"]' in str(exc_info.value)
    assert recorder.calls == []

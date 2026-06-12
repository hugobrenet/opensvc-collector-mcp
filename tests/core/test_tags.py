import pytest

from opensvc_collector_mcp.core.tags import inventory


class CollectorPostRecorder:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def __call__(self, path, data=None, params=None):
        self.calls.append({"path": path, "data": data, "params": params})
        return self.response


async def test_create_tag_posts_writable_tag_fields(monkeypatch):
    recorder = CollectorPostRecorder(
        {
            "meta": {"count": 1},
            "data": [
                {
                    "tag_id": "tag-1",
                    "tag_name": "mcp-test-tag",
                    "tag_data": "created by test",
                    "tag_exclude": None,
                }
            ],
        }
    )
    monkeypatch.setattr(inventory, "collector_post", recorder)

    response = await inventory.create_tag(
        tag_name=" mcp-test-tag ",
        tag_data="created by test",
    )

    assert response["data"][0]["tag_name"] == "mcp-test-tag"
    assert recorder.calls == [
        {
            "path": "/tags",
            "data": {"tag_name": "mcp-test-tag", "tag_data": "created by test"},
            "params": None,
        }
    ]


async def test_create_tag_rejects_empty_tag_name(monkeypatch):
    recorder = CollectorPostRecorder({"meta": {}, "data": []})
    monkeypatch.setattr(inventory, "collector_post", recorder)

    with pytest.raises(ValueError, match="tag_name must not be empty"):
        await inventory.create_tag(tag_name="   ")

    assert recorder.calls == []

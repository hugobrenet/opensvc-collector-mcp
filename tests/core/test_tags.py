import pytest

from opensvc_collector_mcp.core.tags import inventory


class CollectorPostRecorder:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def __call__(self, path, data=None, params=None):
        self.calls.append({"path": path, "data": data, "params": params})
        return self.response


class CollectorGetByPathRecorder:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    async def __call__(self, path, params=None):
        self.calls.append({"path": path, "params": params})
        try:
            return self.responses[path]
        except KeyError as exc:
            raise AssertionError(f"unexpected collector_get path: {path}") from exc


class CollectorDeleteRecorder:
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


async def test_delete_tag_snapshots_confirms_and_deletes_by_tag_id(monkeypatch):
    get_recorder = CollectorGetByPathRecorder(
        {
            "/tags/tag-1": {
                "data": [
                    {
                        "tag_id": "tag-1",
                        "tag_name": "mcp-test-tag",
                        "tag_exclude": None,
                    }
                ],
            },
        }
    )
    delete_recorder = CollectorDeleteRecorder({"meta": {"count": 1}, "data": []})
    monkeypatch.setattr(inventory, "collector_get", get_recorder)
    monkeypatch.setattr(inventory, "collector_delete", delete_recorder)

    response = await inventory.delete_tag(
        tag_id=" tag-1 ",
        confirm_tag_id="tag-1",
        confirm_tag_name=" mcp-test-tag ",
    )

    assert response["deleted"] is True
    assert response["tag_id"] == "tag-1"
    assert response["tag_name"] == "mcp-test-tag"
    assert response["tag"]["tag_name"] == "mcp-test-tag"
    assert response["collector_response"] == {"meta": {"count": 1}, "data": []}
    assert get_recorder.calls == [
        {
            "path": "/tags/tag-1",
            "params": {"props": "tag_id,tag_name,tag_exclude,tag_created,tag_data"},
        }
    ]
    assert delete_recorder.calls == [
        {"path": "/tags/tag-1", "data": None, "params": None}
    ]


async def test_delete_tag_rejects_confirmation_id_mismatch_before_lookup(monkeypatch):
    get_recorder = CollectorGetByPathRecorder({})
    delete_recorder = CollectorDeleteRecorder({"meta": {}, "data": []})
    monkeypatch.setattr(inventory, "collector_get", get_recorder)
    monkeypatch.setattr(inventory, "collector_delete", delete_recorder)

    with pytest.raises(ValueError, match="confirm_tag_id must match tag_id"):
        await inventory.delete_tag(
            tag_id="tag-1",
            confirm_tag_id="other-tag",
            confirm_tag_name="mcp-test-tag",
        )

    assert get_recorder.calls == []
    assert delete_recorder.calls == []


async def test_delete_tag_rejects_confirmation_name_mismatch_before_delete(monkeypatch):
    get_recorder = CollectorGetByPathRecorder(
        {
            "/tags/tag-1": {
                "data": [{"tag_id": "tag-1", "tag_name": "mcp-test-tag"}],
            },
        }
    )
    delete_recorder = CollectorDeleteRecorder({"meta": {}, "data": []})
    monkeypatch.setattr(inventory, "collector_get", get_recorder)
    monkeypatch.setattr(inventory, "collector_delete", delete_recorder)

    with pytest.raises(ValueError, match="confirm_tag_name must match"):
        await inventory.delete_tag(
            tag_id="tag-1",
            confirm_tag_id="tag-1",
            confirm_tag_name="wrong-tag",
        )

    assert [call["path"] for call in get_recorder.calls] == ["/tags/tag-1"]
    assert delete_recorder.calls == []


async def test_delete_tag_quotes_tag_id_path(monkeypatch):
    get_recorder = CollectorGetByPathRecorder(
        {
            "/tags/tag%2F1": {
                "data": [{"tag_id": "tag/1", "tag_name": "mcp-test-tag"}],
            },
        }
    )
    delete_recorder = CollectorDeleteRecorder({"meta": {"count": 1}, "data": []})
    monkeypatch.setattr(inventory, "collector_get", get_recorder)
    monkeypatch.setattr(inventory, "collector_delete", delete_recorder)

    response = await inventory.delete_tag(
        tag_id=" tag/1 ",
        confirm_tag_id="tag/1",
        confirm_tag_name="mcp-test-tag",
    )

    assert response["tag_id"] == "tag/1"
    assert get_recorder.calls == [
        {
            "path": "/tags/tag%2F1",
            "params": {"props": "tag_id,tag_name,tag_exclude,tag_created,tag_data"},
        }
    ]
    assert delete_recorder.calls == [
        {"path": "/tags/tag%2F1", "data": None, "params": None}
    ]


async def test_delete_tag_rejects_ambiguous_tag_id_snapshot(monkeypatch):
    get_recorder = CollectorGetByPathRecorder(
        {
            "/tags/tag-1": {
                "data": [
                    {"tag_id": "tag-1", "tag_name": "mcp-test-tag"},
                    {"tag_id": "tag-1", "tag_name": "mcp-test-tag-copy"},
                ],
            },
        }
    )
    delete_recorder = CollectorDeleteRecorder({"meta": {}, "data": []})
    monkeypatch.setattr(inventory, "collector_get", get_recorder)
    monkeypatch.setattr(inventory, "collector_delete", delete_recorder)

    with pytest.raises(ValueError, match="tag_id resolved to multiple tags"):
        await inventory.delete_tag(
            tag_id="tag-1",
            confirm_tag_id="tag-1",
            confirm_tag_name="mcp-test-tag",
        )

    assert delete_recorder.calls == []


async def test_delete_tag_rejects_tag_name_passed_as_tag_id(monkeypatch):
    get_recorder = CollectorGetByPathRecorder(
        {
            "/tags/mcp-test-tag": {
                "data": [{"tag_id": "tag-1", "tag_name": "mcp-test-tag"}],
            },
        }
    )
    delete_recorder = CollectorDeleteRecorder({"meta": {}, "data": []})
    monkeypatch.setattr(inventory, "collector_get", get_recorder)
    monkeypatch.setattr(inventory, "collector_delete", delete_recorder)

    with pytest.raises(ValueError, match="tag_id must be the exact Collector tag_id"):
        await inventory.delete_tag(
            tag_id="mcp-test-tag",
            confirm_tag_id="mcp-test-tag",
            confirm_tag_name="mcp-test-tag",
        )

    assert get_recorder.calls[0]["path"] == "/tags/mcp-test-tag"
    assert delete_recorder.calls == []

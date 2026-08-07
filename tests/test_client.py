from opensvc_collector_mcp import client
from opensvc_collector_mcp.auth.context import (
    CollectorCredentials,
    reset_collector_credentials,
    set_collector_credentials,
)


async def test_collector_get_uses_request_context_credentials(monkeypatch):
    calls = []

    async def fake_get_with_credentials(path, credentials, params=None):
        calls.append((path, credentials, params))
        return {"data": []}

    monkeypatch.setattr(client, "collector_get_with_credentials", fake_get_with_credentials)

    credentials = CollectorCredentials(username="collector-user", password="secret")
    token = set_collector_credentials(credentials)
    try:
        response = await client.collector_get("/nodes", params={"limit": 1})
    finally:
        reset_collector_credentials(token)

    assert response == {"data": []}
    assert calls == [("/nodes", credentials, {"limit": 1})]


async def test_collector_get_page_returns_lightweight_pagination(monkeypatch):
    calls = []

    async def fake_get(path, params=None):
        calls.append((path, params))
        return {
            "meta": {"total": 42, "available_props": ["nodes.nodename"]},
            "data": [{"nodename": "node-a"}, {"nodename": "node-b"}],
        }

    monkeypatch.setattr(client, "collector_get", fake_get)

    response = await client.collector_get_page(
        "/nodes",
        params={"props": "nodename", "meta": True},
        limit=2,
        offset=4,
    )

    assert calls == [
        (
            "/nodes",
            {"props": "nodename", "meta": False, "limit": 2, "offset": 4},
        )
    ]
    assert response == {
        "pagination": {
            "limit": 2,
            "offset": 4,
            "returned": 2,
            "next_offset": 6,
            "complete": False,
            "truncated": False,
        },
        "data": [{"nodename": "node-a"}, {"nodename": "node-b"}],
    }


async def test_collector_get_page_preserves_repeated_filters_and_stops_on_short_page(
    monkeypatch,
):
    calls = []

    async def fake_get(path, params=None):
        calls.append((path, params))
        return {"data": [{"nodename": "node-a"}]}

    monkeypatch.setattr(client, "collector_get", fake_get)

    response = await client.collector_get_page(
        "/nodes",
        params=[
            ("filters", "type=physical"),
            ("filters", "asset_env=PRD"),
            ("limit", 999),
            ("meta", True),
        ],
        limit=2,
        offset=8,
    )

    assert calls == [
        (
            "/nodes",
            [
                ("filters", "type=physical"),
                ("filters", "asset_env=PRD"),
                ("limit", 2),
                ("offset", 8),
                ("meta", False),
            ],
        )
    ]
    assert response["pagination"] == {
        "limit": 2,
        "offset": 8,
        "returned": 1,
        "next_offset": None,
        "complete": True,
        "truncated": False,
    }


async def test_collector_get_page_infers_limit_and_offset_from_params(monkeypatch):
    calls = []

    async def fake_get(path, params=None):
        calls.append((path, params))
        return {"data": []}

    monkeypatch.setattr(client, "collector_get", fake_get)

    response = await client.collector_get_page(
        "/nodes",
        params=[("limit", 5), ("offset", 15)],
    )

    assert calls == [
        (
            "/nodes",
            [("limit", 5), ("offset", 15), ("meta", False)],
        )
    ]
    assert response["pagination"] == {
        "limit": 5,
        "offset": 15,
        "returned": 0,
        "next_offset": None,
        "complete": True,
        "truncated": False,
    }


async def test_collector_get_all_stops_on_short_page(monkeypatch):
    calls = []
    responses = [
        {
            "pagination": {
                "limit": 2,
                "offset": 0,
                "returned": 2,
                "next_offset": 2,
                "complete": False,
            },
            "data": [{"id": 1}, {"id": 2}],
        },
        {
            "pagination": {
                "limit": 2,
                "offset": 2,
                "returned": 1,
                "next_offset": None,
                "complete": True,
            },
            "data": [{"id": 3}],
        },
    ]

    async def fake_page(path, params=None, *, limit=None, offset=None):
        calls.append((path, params, limit, offset))
        return responses.pop(0)

    monkeypatch.setattr(client, "collector_get_page", fake_page)

    response = await client.collector_get_all(
        "/nodes",
        params=[("filters", "type=physical")],
        page_size=2,
        max_items=10,
    )

    assert calls == [
        ("/nodes", [("filters", "type=physical")], 2, 0),
        ("/nodes", [("filters", "type=physical")], 2, 2),
    ]
    assert response == {
        "meta": {
            "count": 3,
            "total": 3,
            "offset": 0,
            "complete": True,
            "truncated": False,
            "max_items": 10,
            "scanned": 3,
        },
        "data": [{"id": 1}, {"id": 2}, {"id": 3}],
    }


async def test_collector_get_all_marks_max_items_as_truncated(monkeypatch):
    async def fake_page(path, params=None, *, limit=None, offset=None):
        return {
            "pagination": {
                "limit": limit,
                "offset": offset,
                "returned": limit,
                "next_offset": offset + limit,
                "complete": False,
            },
            "data": [{"id": index} for index in range(offset, offset + limit)],
        }

    monkeypatch.setattr(client, "collector_get_page", fake_page)

    response = await client.collector_get_all(
        "/nodes",
        page_size=2,
        max_items=3,
    )

    assert response["meta"] == {
        "count": 3,
        "total": None,
        "offset": 0,
        "complete": False,
        "truncated": True,
        "max_items": 3,
        "scanned": 3,
    }
    assert response["data"] == [{"id": 0}, {"id": 1}, {"id": 2}]


async def test_collector_put_uses_request_context_credentials(monkeypatch):
    calls = []

    async def fake_put_with_credentials(path, credentials, data=None, params=None):
        calls.append((path, credentials, data, params))
        return {"data": []}

    monkeypatch.setattr(client, "collector_put_with_credentials", fake_put_with_credentials)

    credentials = CollectorCredentials(username="collector-user", password="secret")
    token = set_collector_credentials(credentials)
    try:
        response = await client.collector_put(
            "/actions",
            data={"node_id": "node-a-id", "action": "freeze"},
        )
    finally:
        reset_collector_credentials(token)

    assert response == {"data": []}
    assert calls == [
        (
            "/actions",
            credentials,
            {"node_id": "node-a-id", "action": "freeze"},
            None,
        )
    ]


async def test_collector_delete_uses_request_context_credentials(monkeypatch):
    calls = []

    async def fake_delete_with_credentials(path, credentials, data=None, params=None):
        calls.append((path, credentials, data, params))
        return {"data": []}

    monkeypatch.setattr(
        client,
        "collector_delete_with_credentials",
        fake_delete_with_credentials,
    )

    credentials = CollectorCredentials(username="collector-user", password="secret")
    token = set_collector_credentials(credentials)
    try:
        response = await client.collector_delete(
            "/tags/tag-1",
            params={"reason": "test"},
        )
    finally:
        reset_collector_credentials(token)

    assert response == {"data": []}
    assert calls == [("/tags/tag-1", credentials, None, {"reason": "test"})]


async def test_collector_put_with_credentials_uses_put(monkeypatch):
    calls = []

    class FakeResponse:
        def raise_for_status(self):
            calls.append(("raise_for_status",))

        def json(self):
            return {"info": "queued"}

    class FakeAsyncClient:
        def __init__(self, **kwargs):
            calls.append(("init", kwargs))

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def put(self, url, **kwargs):
            calls.append(("put", url, kwargs))
            return FakeResponse()

    monkeypatch.setattr(client, "OPENSVC_API_BASE_URL", "https://collector.example/api")
    monkeypatch.setattr(client.httpx, "AsyncClient", FakeAsyncClient)

    credentials = CollectorCredentials(username="collector-user", password="secret")
    response = await client.collector_put_with_credentials(
        "/actions",
        credentials=credentials,
        data={"node_id": "node-a-id", "action": "freeze"},
        params={"dry": "false"},
    )

    assert response == {"info": "queued"}
    assert calls[0][0] == "init"
    assert calls[1] == (
        "put",
        "https://collector.example/api/actions",
        {
            "params": {"dry": "false"},
            "data": {"node_id": "node-a-id", "action": "freeze"},
            "auth": ("collector-user", "secret"),
            "headers": {"Accept": "application/json"},
        },
    )
    assert calls[2] == ("raise_for_status",)


async def test_collector_delete_with_credentials_uses_generic_request(monkeypatch):
    calls = []

    class FakeResponse:
        def raise_for_status(self):
            calls.append(("raise_for_status",))

        def json(self):
            return {"info": "deleted"}

    class FakeAsyncClient:
        def __init__(self, **kwargs):
            calls.append(("init", kwargs))

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def request(self, method, url, **kwargs):
            calls.append(("request", method, url, kwargs))
            return FakeResponse()

    monkeypatch.setattr(client, "OPENSVC_API_BASE_URL", "https://collector.example/api")
    monkeypatch.setattr(client.httpx, "AsyncClient", FakeAsyncClient)

    credentials = CollectorCredentials(username="collector-user", password="secret")
    response = await client.collector_delete_with_credentials(
        "/tags/tag-1",
        credentials=credentials,
        data={"reason": "test"},
        params={"dry": "false"},
    )

    assert response == {"info": "deleted"}
    assert calls[0][0] == "init"
    assert calls[1] == (
        "request",
        "DELETE",
        "https://collector.example/api/tags/tag-1",
        {
            "params": {"dry": "false"},
            "data": {"reason": "test"},
            "auth": ("collector-user", "secret"),
            "headers": {"Accept": "application/json"},
        },
    )
    assert calls[2] == ("raise_for_status",)


async def test_collector_get_requires_request_context_credentials():
    try:
        await client.collector_get("/nodes")
    except RuntimeError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected missing credentials to raise")

    assert "Missing Collector Basic Auth credentials" in message

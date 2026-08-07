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

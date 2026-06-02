from opensvc_collector_mcp import client
from opensvc_collector_mcp.client import (
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


async def test_get_collector_group_roles_returns_group_roles(monkeypatch):
    async def fake_collector_get_all(path, params=None, page_size=1000, max_items=200000):
        return {
            "data": [
                {"id": 1, "role": "Everybody", "privilege": "F"},
                {"id": 2, "role": "Manager", "privilege": "T"},
                {"id": 3, "privilege": "F"},
            ]
        }

    monkeypatch.setattr(client, "collector_get_all", fake_collector_get_all)

    roles = await client.get_collector_group_roles()

    assert roles == {"Everybody", "Manager"}


async def test_collector_get_requires_request_context_credentials():
    try:
        await client.collector_get("/nodes")
    except RuntimeError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected missing credentials to raise")

    assert "Missing Collector Basic Auth credentials" in message

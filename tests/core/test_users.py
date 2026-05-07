from opensvc_collector_mcp.core.users import inventory


async def test_list_users_builds_collection_params(monkeypatch, collector_mock_factory):
    collector = collector_mock_factory([{"meta": {"total": 1}, "data": [{"username": "user-a"}]}])
    monkeypatch.setattr(inventory, "collector_get", collector.get)

    response = await inventory.list_users(
        filters={"username": "user-a"},
        props="id,username,email",
        orderby="username",
        search="user-a",
        limit=5,
        offset=1,
    )

    assert response["data"] == [{"username": "user-a"}]
    call = collector.calls[0]
    assert call.path == "/users"
    assert call.single_param("limit") == 5
    assert call.single_param("offset") == 1
    assert call.single_param("props") == "id,username,email"
    assert call.single_param("orderby") == "username"
    assert call.single_param("search") == "user-a"
    assert call.param_values("filters") == ["username=user-a"]


async def test_count_users_uses_lightweight_total_query(monkeypatch, collector_mock_factory):
    collector = collector_mock_factory([{"meta": {"total": 12}, "data": []}])
    monkeypatch.setattr(inventory, "collector_get", collector.get)

    response = await inventory.count_users(filters={"lock_filter": "False"})

    assert response == {
        "count": 12,
        "filters": {"lock_filter": "False"},
        "search": None,
    }
    call = collector.calls[0]
    assert call.path == "/users"
    assert call.single_param("limit") == 1
    assert call.single_param("offset") == 0
    assert call.single_param("props") == "id"
    assert call.param_values("filters") == ["lock_filter=False"]


async def test_get_user_resolves_username_and_includes_relations(monkeypatch, collector_mock_factory):
    collector = collector_mock_factory([
        {"meta": {"total": 0}, "data": []},
        {"meta": {"total": 1}, "data": [{"id": 42, "username": "user-a", "email": "user@example.invalid"}]},
        {"meta": {}, "data": [{"id": 42, "username": "user-a"}]},
        {"meta": {}, "data": [{"id": 1, "role": "PRIMARY"}]},
        {"meta": {}, "data": [{"id": 2, "role": "GROUP"}]},
    ])
    monkeypatch.setattr(inventory, "collector_get", collector.get)

    response = await inventory.get_user(
        "user-a",
        props="id,username,email",
        include_primary_group=True,
        include_groups=True,
        group_props="id,role",
    )

    assert response["meta"]["resolved_id"] == 42
    assert response["meta"]["resolution"] == "username"
    assert response["primary_group"] == [{"id": 1, "role": "PRIMARY"}]
    assert response["groups"] == [{"id": 2, "role": "GROUP"}]
    assert [call.path for call in collector.calls] == [
        "/users",
        "/users",
        "/users/42",
        "/users/42/primary_group",
        "/users/42/groups",
    ]
    assert collector.calls[0].param_values("filters") == ["email=user-a"]
    assert collector.calls[1].param_values("filters") == ["username=user-a"]
    assert collector.calls[2].params == {"props": "id,username,email"}
    assert collector.calls[3].params == {"props": "id,role", "limit": 1000, "offset": 0}
    assert collector.calls[4].params == {"props": "id,role", "limit": 1000, "offset": 0}


async def test_get_user_self_uses_self_dump(monkeypatch, collector_mock_factory):
    collector = collector_mock_factory([
        {"user": [{"id": 7, "username": "self-user", "email": "self@example.invalid"}]}
    ])
    monkeypatch.setattr(inventory, "collector_get", collector.get)

    response = await inventory.get_user("self")

    assert response["meta"]["source"] == "users_self_dump"
    assert response["meta"]["resolved_id"] == 7
    assert response["data"] == [{"id": 7, "username": "self-user", "email": "self@example.invalid"}]
    assert collector.calls[0].path == "/users/self/dump"


async def test_search_users_by_group_scans_users_and_matches_group(monkeypatch, collector_mock_factory):
    get_all_calls = []

    async def fake_get_all(path, params=None, page_size=1000, max_items=5000):
        get_all_calls.append(
            {"path": path, "params": params, "page_size": page_size, "max_items": max_items}
        )
        return {
            "meta": {"complete": True, "total": 2},
            "data": [{"id": 1, "username": "user-a"}, {"id": 2, "username": "user-b"}],
        }

    collector = collector_mock_factory([
        {"meta": {}, "data": [{"role": "GROUP-A"}]},
        {"meta": {}, "data": [{"role": "GROUP-B"}]},
    ])
    monkeypatch.setattr(inventory, "collector_get_all", fake_get_all)
    monkeypatch.setattr(inventory, "collector_get", collector.get)

    response = await inventory.search_users_by_group(
        "GROUP-A",
        filters={"lock_filter": "False"},
        props="id,username",
        max_users=10,
    )

    assert response["meta"]["matched_users"] == 1
    assert response["data"] == [
        {"id": 1, "username": "user-a", "matched_group": {"role": "GROUP-A"}}
    ]
    assert get_all_calls[0]["path"] == "/users"
    assert get_all_calls[0]["max_items"] == 10
    assert collector.calls[0].path == "/users/1/groups"
    assert collector.calls[1].path == "/users/2/groups"

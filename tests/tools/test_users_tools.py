from opensvc_collector_mcp.tools import users as user_tools


class CoreRecorder:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def __call__(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


async def test_list_users_tool_passes_request_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder(
        {
            "pagination": {
                "limit": 5,
                "offset": 2,
                "returned": 1,
                "next_offset": None,
                "complete": True,
            },
            "data": [{"username": "user-a"}],
        }
    )
    monkeypatch.setattr(user_tools, "core_list_users", recorder)

    result = await mcp_client.call_tool(
        "list_users",
        {
            "request": {
                "username": "user-a",
                "props": "id,username,email",
                "orderby": "username",
                "search": "user-a",
                "limit": 5,
                "offset": 2,
            }
        },
    )

    assert result.structured_content["data"][0]["username"] == "user-a"
    assert recorder.calls == [
        {
            "filters": {"username": "user-a"},
            "props": "id,username,email",
            "orderby": "username",
            "search": "user-a",
            "limit": 5,
            "offset": 2,
        }
    ]


async def test_count_users_tool_passes_filters_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder({"count": 1, "filters": {"username": "user-a"}, "search": None})
    monkeypatch.setattr(user_tools, "core_count_users", recorder)

    result = await mcp_client.call_tool(
        "count_users",
        {"request": {"username": "user-a"}},
    )

    assert result.structured_content == {
        "count": 1,
        "filters": {"username": "user-a"},
        "search": None,
    }
    assert recorder.calls == [{"filters": {"username": "user-a"}, "search": None}]


async def test_get_user_tool_passes_relation_flags_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder(
        {
            "meta": {"resolved_id": 42},
            "data": [{"id": 42, "username": "user-a"}],
            "primary_group": [{"id": 1, "role": "PRIMARY"}],
            "groups": [{"id": 2, "role": "GROUP"}],
        }
    )
    monkeypatch.setattr(user_tools, "core_get_user", recorder)

    result = await mcp_client.call_tool(
        "get_user",
        {
            "request": {
                "user": "user-a",
                "props": "id,username,email",
                "include_primary_group": True,
                "include_groups": True,
                "group_props": "id,role",
            }
        },
    )

    assert result.structured_content["data"][0]["username"] == "user-a"
    assert result.structured_content["primary_group"][0]["role"] == "PRIMARY"
    assert recorder.calls == [
        {
            "user": "user-a",
            "props": "id,username,email",
            "include_primary_group": True,
            "include_groups": True,
            "group_props": "id,role",
        }
    ]


async def test_search_users_by_group_tool_passes_scan_request_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder(
        {
            "meta": {"group": "GROUP", "matched_users": 1},
            "data": [
                {
                    "id": 42,
                    "username": "user-a",
                    "matched_group": {"id": 2, "role": "GROUP"},
                }
            ],
        }
    )
    monkeypatch.setattr(user_tools, "core_search_users_by_group", recorder)

    result = await mcp_client.call_tool(
        "search_users_by_group",
        {
            "request": {
                "group": "GROUP",
                "username": "user-a",
                "props": "id,username",
                "max_users": 100,
            }
        },
    )

    assert result.structured_content["data"][0]["matched_group"]["role"] == "GROUP"
    assert recorder.calls == [
        {
            "group": "GROUP",
            "filters": {"username": "user-a"},
            "props": "id,username",
            "orderby": None,
            "search": None,
            "max_users": 100,
        }
    ]


async def test_count_users_by_primary_group_tool_passes_scan_request_to_core(monkeypatch, mcp_client):
    recorder = CoreRecorder(
        {
            "count": 3,
            "primary_group": "PRIMARY",
            "filters": {"lock_filter": "False"},
            "search": None,
            "scanned_users": 10,
            "max_users": 100,
            "complete": True,
            "collector_total": 10,
        }
    )
    monkeypatch.setattr(user_tools, "core_count_users_by_primary_group", recorder)

    result = await mcp_client.call_tool(
        "count_users_by_primary_group",
        {
            "request": {
                "primary_group": "PRIMARY",
                "lock_filter": "False",
                "max_users": 100,
            }
        },
    )

    assert result.structured_content["count"] == 3
    assert recorder.calls == [
        {
            "primary_group": "PRIMARY",
            "filters": {"lock_filter": "False"},
            "orderby": None,
            "search": None,
            "max_users": 100,
        }
    ]

import asyncio
from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get, collector_get_all
from opensvc_collector_mcp.core.utils import collection_params, parse_collector_filters


DEFAULT_LIST_USER_PROPS = (
    "id,username,email,first_name,last_name,lock_filter,"
    "quota_app,quota_org_group,quota_docker_registries"
)
DEFAULT_PRIMARY_GROUP_SEARCH_USER_PROPS = (
    "id,username,email,first_name,last_name,lock_filter"
)
PRIMARY_GROUP_PROPS = "id,role,description,privilege"


async def list_users(
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "email",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    selected_props = props or DEFAULT_LIST_USER_PROPS
    parsed_filters = _user_search_filters(filters)
    return await collector_get(
        "/users",
        params=collection_params(
            filters=parsed_filters,
            props=selected_props,
            orderby=orderby,
            search=search,
            limit=limit,
            offset=offset,
        ),
    )


async def list_user_props() -> dict[str, Any]:
    response = await collector_get("/users", params={"props": "id", "limit": 1})
    available_props = response.get("meta", {}).get("available_props", [])
    user_props = [
        prop.removeprefix("auth_user.")
        for prop in available_props
        if isinstance(prop, str)
    ]

    return {
        "count": len(available_props),
        "available_props": available_props,
        "user_props": user_props,
    }


async def search_users_by_primary_group(
    primary_group: str,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "email",
    search: str | None = None,
    max_users: int = 5000,
) -> dict[str, Any]:
    primary_group = primary_group.strip()
    if not primary_group:
        raise ValueError("primary_group must not be empty")

    max_users = max(1, min(max_users, 50000))
    selected_props = _props_with_required(
        props or DEFAULT_PRIMARY_GROUP_SEARCH_USER_PROPS, "id"
    )
    parsed_filters = _user_search_filters(filters)

    users_response = await collector_get_all(
        "/users",
        params=collection_params(
            filters=parsed_filters,
            props=selected_props,
            orderby=orderby,
            search=search,
            limit=1000,
            offset=0,
        ),
        page_size=1000,
        max_items=max_users,
    )
    users = users_response.get("data", [])

    primary_groups = await _get_primary_groups_for_users(users)
    matches: list[dict[str, Any]] = []
    for user in users:
        user_id = str(user.get("id") or "").strip()
        groups = primary_groups.get(user_id, [])
        for group in groups:
            if str(group.get("role") or "") == primary_group:
                item = dict(user)
                item["primary_group"] = group
                matches.append(item)
                break

    users_meta = users_response.get("meta", {})
    complete = bool(users_meta.get("complete", True))
    return {
        "meta": {
            "source": "users_primary_group",
            "primary_group": primary_group,
            "filter": {field: value for field, value in parsed_filters},
            "included_props": selected_props.split(","),
            "scanned_users": len(users),
            "matched_users": len(matches),
            "max_users": max_users,
            "complete": complete,
            "collector_total": users_meta.get("total"),
        },
        "data": matches,
    }


def _props_with_required(props: str, *required_props: str) -> str:
    selected = [prop.strip() for prop in props.split(",") if prop.strip()]
    for prop in required_props:
        if prop not in selected:
            selected.append(prop)
    return ",".join(selected)


async def _get_primary_groups_for_users(
    users: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    semaphore = asyncio.Semaphore(20)

    async def get_one(user: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
        user_id = str(user.get("id") or "").strip()
        if not user_id:
            return "", []
        encoded_user_id = quote(user_id, safe="")
        async with semaphore:
            response = await collector_get(
                f"/users/{encoded_user_id}/primary_group",
                params={"props": PRIMARY_GROUP_PROPS},
            )
        rows = response.get("data", [])
        if not isinstance(rows, list):
            rows = []
        return user_id, rows

    results = await asyncio.gather(*(get_one(user) for user in users))
    return {user_id: rows for user_id, rows in results if user_id}


def _user_search_filters(
    raw_filters: dict[str, str] | str | None = None,
    **criteria: str | None,
) -> list[tuple[str, str]]:
    filters = parse_collector_filters(raw_filters)
    for field, value in criteria.items():
        if value is None:
            continue
        value = value.strip()
        if value:
            filters.append((field, value))
    return filters

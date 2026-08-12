import asyncio
from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get, collector_get_all
from opensvc_collector_mcp.core.utils import collection_params

from ._common import props_with_required, user_search_filters


DEFAULT_RELATION_SEARCH_USER_PROPS = (
    "id,username,email,first_name,last_name,lock_filter"
)
DEFAULT_USER_GROUP_PROPS = "id,role,description,privilege"


async def get_user_relation(
    selector: str,
    relation: str,
    props: str,
) -> list[dict[str, Any]]:
    encoded_selector = quote(selector, safe="")
    response = await collector_get(
        f"/users/{encoded_selector}/{relation}",
        params={"props": props, "limit": 1000, "offset": 0},
    )
    rows = response.get("data", [])
    return rows if isinstance(rows, list) else []


async def search_users_by_relation(
    *,
    relation: str,
    role: str,
    role_meta_key: str,
    source: str,
    match_key: str,
    filters: dict[str, str] | str | None,
    props: str | None,
    orderby: str | None,
    search: str | None,
    max_users: int,
) -> dict[str, Any]:
    max_users = max(1, min(max_users, 50000))
    selected_props = props_with_required(
        props or DEFAULT_RELATION_SEARCH_USER_PROPS,
        "id",
    )
    parsed_filters = user_search_filters(filters)

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
    relations = await _get_relations_for_users(users, relation=relation)

    matches: list[dict[str, Any]] = []
    for user in users:
        user_id = str(user.get("id") or "").strip()
        for related_group in relations.get(user_id, []):
            if str(related_group.get("role") or "") == role:
                item = dict(user)
                item[match_key] = related_group
                matches.append(item)
                break

    users_meta = users_response.get("meta", {})
    return {
        "meta": {
            "source": source,
            role_meta_key: role,
            "filter": {field: value for field, value in parsed_filters},
            "included_props": selected_props.split(","),
            "scanned_users": len(users),
            "matched_users": len(matches),
            "max_users": max_users,
            "complete": bool(users_meta.get("complete", True)),
            "collector_total": users_meta.get("total"),
        },
        "data": matches,
    }


async def _get_relations_for_users(
    users: list[dict[str, Any]],
    *,
    relation: str,
) -> dict[str, list[dict[str, Any]]]:
    semaphore = asyncio.Semaphore(20)

    async def get_one(user: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
        user_id = str(user.get("id") or "").strip()
        if not user_id:
            return "", []
        async with semaphore:
            rows = await get_user_relation(
                selector=user_id,
                relation=relation,
                props=DEFAULT_USER_GROUP_PROPS,
            )
        return user_id, rows

    results = await asyncio.gather(*(get_one(user) for user in users))
    return {user_id: rows for user_id, rows in results if user_id}

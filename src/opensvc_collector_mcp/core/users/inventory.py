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
DEFAULT_USER_GROUP_PROPS = "id,role,description,privilege"


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


async def get_user(
    user: str,
    props: str | None = None,
    include_primary_group: bool = False,
    include_groups: bool = False,
    group_props: str | None = None,
) -> dict[str, Any]:
    selector = user.strip()
    if not selector:
        raise ValueError("user must not be empty")

    relation_selector = selector
    if selector == "self":
        response = await collector_get("/users/self/dump")
        rows = response.get("user", [])
        row = rows[0] if isinstance(rows, list) and rows else {}
        relation_selector = str(row.get("id") or selector)
        meta = {
            "source": "users_self_dump",
            "selector": selector,
            "resolved_id": row.get("id"),
            "resolved_username": row.get("username"),
            "resolved_email": row.get("email"),
            "count": len(rows) if isinstance(rows, list) else 0,
        }
    else:
        resolved = await _resolve_user_selector(selector)
        detail_selector = resolved.get("id") or selector
        relation_selector = str(detail_selector)
        encoded_selector = quote(str(detail_selector), safe="")
        params = {"props": props} if props else None
        response = await collector_get(f"/users/{encoded_selector}", params=params)
        rows = response.get("data", [])
        meta = dict(response.get("meta", {}))
        meta.update(
            {
                "source": "users_detail",
                "selector": selector,
                "resolved_id": resolved.get("id"),
                "resolved_username": resolved.get("username"),
                "resolved_email": resolved.get("email"),
                "resolution": resolved.get("resolution"),
                "count": len(rows) if isinstance(rows, list) else 0,
            }
        )

    result: dict[str, Any] = {
        "meta": meta,
        "data": rows if isinstance(rows, list) else [],
    }

    relation_props = group_props or DEFAULT_USER_GROUP_PROPS
    if include_primary_group:
        result["primary_group"] = await _get_user_relation(
            selector=relation_selector,
            relation="primary_group",
            props=relation_props,
        )
    if include_groups:
        result["groups"] = await _get_user_relation(
            selector=relation_selector,
            relation="groups",
            props=relation_props,
        )

    return result


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


async def _resolve_user_selector(selector: str) -> dict[str, Any]:
    if selector.isdigit():
        return {"id": selector, "resolution": "id"}

    lookup_props = "id,username,email"
    for field in ("email", "username"):
        response = await collector_get(
            "/users",
            params=collection_params(
                filters=[(field, selector)],
                props=lookup_props,
                orderby=None,
                search=None,
                limit=2,
                offset=0,
            ),
        )
        rows = response.get("data", [])
        if not isinstance(rows, list) or not rows:
            continue
        exact_rows = [row for row in rows if str(row.get(field) or "") == selector]
        if len(exact_rows) == 1:
            row = exact_rows[0]
            return {
                "id": row.get("id"),
                "username": row.get("username"),
                "email": row.get("email"),
                "resolution": field,
            }
        if len(exact_rows) > 1:
            raise ValueError(
                f"user selector {selector!r} matched multiple users by {field}"
            )

    return {"id": selector, "resolution": "direct"}


def _props_with_required(props: str, *required_props: str) -> str:
    selected = [prop.strip() for prop in props.split(",") if prop.strip()]
    for prop in required_props:
        if prop not in selected:
            selected.append(prop)
    return ",".join(selected)


async def _get_user_relation(selector: str, relation: str, props: str) -> list[dict[str, Any]]:
    encoded_selector = quote(selector, safe="")
    response = await collector_get(
        f"/users/{encoded_selector}/{relation}",
        params={"props": props, "limit": 1000, "offset": 0},
    )
    rows = response.get("data", [])
    return rows if isinstance(rows, list) else []


async def _get_primary_groups_for_users(
    users: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    semaphore = asyncio.Semaphore(20)

    async def get_one(user: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
        user_id = str(user.get("id") or "").strip()
        if not user_id:
            return "", []
        async with semaphore:
            rows = await _get_user_relation(
                selector=user_id,
                relation="primary_group",
                props=DEFAULT_USER_GROUP_PROPS,
            )
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

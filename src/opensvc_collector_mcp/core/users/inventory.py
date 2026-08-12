from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get, collector_get_page
from opensvc_collector_mcp.core.collection import collection_params

from ._common import user_search_filters
from ._relations import DEFAULT_USER_GROUP_PROPS, get_user_relation


DEFAULT_LIST_USER_PROPS = (
    "id,username,email,first_name,last_name,lock_filter,"
    "quota_app,quota_org_group,quota_docker_registries"
)


async def list_users(
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "email",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    selected_props = props or DEFAULT_LIST_USER_PROPS
    parsed_filters = user_search_filters(filters)
    return await collector_get_page(
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


async def count_users(
    filters: dict[str, str] | str | None = None,
    search: str | None = None,
) -> dict[str, Any]:
    parsed_filters = user_search_filters(filters)
    response = await collector_get(
        "/users",
        params=collection_params(
            filters=parsed_filters,
            props="id",
            orderby=None,
            search=search,
            limit=1,
            offset=0,
        ),
    )
    meta = response.get("meta", {})
    return {
        "count": meta.get("total"),
        "filters": {field: value for field, value in parsed_filters},
        "search": search,
    }


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
        result["primary_group"] = await get_user_relation(
            selector=relation_selector,
            relation="primary_group",
            props=relation_props,
        )
    if include_groups:
        result["groups"] = await get_user_relation(
            selector=relation_selector,
            relation="groups",
            props=relation_props,
        )

    return result


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

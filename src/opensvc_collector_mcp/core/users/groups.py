from typing import Any

from ._relations import search_users_by_relation


async def search_users_by_group(
    group: str,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "email",
    search: str | None = None,
    max_users: int = 5000,
) -> dict[str, Any]:
    group = group.strip()
    if not group:
        raise ValueError("group must not be empty")

    return await search_users_by_relation(
        relation="groups",
        role=group,
        role_meta_key="group",
        source="users_group",
        match_key="matched_group",
        filters=filters,
        props=props,
        orderby=orderby,
        search=search,
        max_users=max_users,
    )


async def count_users_by_group(
    group: str,
    filters: dict[str, str] | str | None = None,
    orderby: str | None = "email",
    search: str | None = None,
    max_users: int = 5000,
) -> dict[str, Any]:
    response = await search_users_by_group(
        group=group,
        filters=filters,
        props="id",
        orderby=orderby,
        search=search,
        max_users=max_users,
    )
    meta = response.get("meta", {})
    return {
        "count": meta.get("matched_users"),
        "group": group,
        "filters": meta.get("filter", {}),
        "search": search,
        "scanned_users": meta.get("scanned_users"),
        "max_users": meta.get("max_users"),
        "complete": meta.get("complete"),
        "collector_total": meta.get("collector_total"),
    }

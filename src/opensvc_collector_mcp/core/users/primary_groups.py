from typing import Any

from ._relations import search_users_by_relation


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

    return await search_users_by_relation(
        relation="primary_group",
        role=primary_group,
        role_meta_key="primary_group",
        source="users_primary_group",
        match_key="primary_group",
        filters=filters,
        props=props,
        orderby=orderby,
        search=search,
        max_users=max_users,
    )


async def count_users_by_primary_group(
    primary_group: str,
    filters: dict[str, str] | str | None = None,
    orderby: str | None = "email",
    search: str | None = None,
    max_users: int = 5000,
) -> dict[str, Any]:
    response = await search_users_by_primary_group(
        primary_group=primary_group,
        filters=filters,
        props="id",
        orderby=orderby,
        search=search,
        max_users=max_users,
    )
    meta = response.get("meta", {})
    return {
        "count": meta.get("matched_users"),
        "primary_group": primary_group,
        "filters": meta.get("filter", {}),
        "search": search,
        "scanned_users": meta.get("scanned_users"),
        "max_users": meta.get("max_users"),
        "complete": meta.get("complete"),
        "collector_total": meta.get("collector_total"),
    }

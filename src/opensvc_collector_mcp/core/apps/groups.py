from typing import Any

from ._relations import get_app_relation_page


DEFAULT_APP_GROUP_PROPS = "id,role,privilege,description"


async def get_app_responsibles(
    app: str,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "role",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    return await _get_app_group_relation(
        app=app,
        relation="responsibles",
        filters=filters,
        props=props,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )


async def get_app_publications(
    app: str,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "role",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    return await _get_app_group_relation(
        app=app,
        relation="publications",
        filters=filters,
        props=props,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )


async def _get_app_group_relation(
    app: str,
    relation: str,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "role",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    if relation not in {"responsibles", "publications"}:
        raise ValueError(f"unsupported app group relation: {relation}")
    return await get_app_relation_page(
        app=app,
        relation=relation,
        filters=filters,
        props=props or DEFAULT_APP_GROUP_PROPS,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )

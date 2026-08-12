from typing import Any

from ._relations import get_app_relation_page


DEFAULT_APP_QUOTA_PROPS = (
    "app,array_name,array_model,dg_name,quota,quota_used,"
    "dg_size,dg_used,dg_free,dg_reserved,dg_reservable"
)


async def get_app_quotas(
    app: str,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "array_name",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    return await get_app_relation_page(
        app=app,
        relation="quotas",
        filters=filters,
        props=props or DEFAULT_APP_QUOTA_PROPS,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )

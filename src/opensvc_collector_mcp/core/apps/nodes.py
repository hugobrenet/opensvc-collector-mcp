from typing import Any

from ._relations import count_app_relation, get_app_relation_page


DEFAULT_APP_NODE_PROPS = (
    "nodename,status,asset_env,node_env,app,team_responsible,os_name"
)


async def get_app_nodes(
    app: str,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "nodename",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    return await get_app_relation_page(
        app=app,
        relation="nodes",
        filters=filters,
        props=props or DEFAULT_APP_NODE_PROPS,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )


async def count_app_nodes(
    app: str,
) -> dict[str, Any]:
    return await count_app_relation(
        app=app,
        relation="nodes",
        props="nodename",
    )

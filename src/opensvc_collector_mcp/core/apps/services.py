from typing import Any

from ._relations import count_app_relation, get_app_relation_page


DEFAULT_APP_SERVICE_PROPS = (
    "svcname,svc_app,svc_env,svc_status,svc_availstatus,svc_topology,"
    "svc_nodes,svc_drpnodes,svc_frozen,svc_ha,svc_created,updated"
)


async def get_app_services(
    app: str,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "svcname",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    return await get_app_relation_page(
        app=app,
        relation="services",
        filters=filters,
        props=props or DEFAULT_APP_SERVICE_PROPS,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )


async def count_app_services(
    app: str,
) -> dict[str, Any]:
    return await count_app_relation(
        app=app,
        relation="services",
        props="svcname",
    )

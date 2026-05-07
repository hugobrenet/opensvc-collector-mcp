from typing import Any

from opensvc_collector_mcp.client import collector_get
from opensvc_collector_mcp.core.utils import collection_params, parse_collector_filters


DEFAULT_LIST_APP_PROPS = "app,app_domain,app_team_ops,description,updated"


async def list_apps(
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "app",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    selected_props = props or DEFAULT_LIST_APP_PROPS
    parsed_filters = parse_collector_filters(filters)
    return await collector_get(
        "/apps",
        params=collection_params(
            filters=parsed_filters,
            props=selected_props,
            orderby=orderby,
            search=search,
            limit=limit,
            offset=offset,
        ),
    )


async def list_app_props() -> dict[str, Any]:
    response = await collector_get("/apps", params={"props": "app", "limit": 1})
    available_props = response.get("meta", {}).get("available_props", [])
    app_props = [
        prop.removeprefix("apps.")
        for prop in available_props
        if isinstance(prop, str)
    ]

    return {
        "count": len(available_props),
        "available_props": available_props,
        "app_props": app_props,
    }

from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get, collector_get_all
from opensvc_collector_mcp.core.utils import collection_params, parse_collector_filters


DEFAULT_LIST_APP_PROPS = "app,app_domain,app_team_ops,description,updated"
DEFAULT_APP_NODE_PROPS = (
    "nodename,status,asset_env,node_env,app,team_responsible,os_name"
)


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


async def get_app(
    app: str,
    props: str | None = None,
) -> dict[str, Any]:
    selector = app.strip()
    if not selector:
        raise ValueError("app must not be empty")

    params = {"props": props} if props else None
    response = await collector_get(
        f"/apps/{quote(selector, safe='')}",
        params=params,
    )
    rows = response.get("data", [])
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "app_detail",
            "selector": selector,
            "count": len(rows) if isinstance(rows, list) else 0,
        }
    )
    return {"meta": meta, "data": rows if isinstance(rows, list) else []}


async def get_app_nodes(
    app: str,
    props: str | None = None,
    max_nodes: int = 200000,
) -> dict[str, Any]:
    selector = app.strip()
    if not selector:
        raise ValueError("app must not be empty")

    selected_props = props or DEFAULT_APP_NODE_PROPS
    response = await collector_get_all(
        f"/apps/{quote(selector, safe='')}/nodes",
        params={"props": selected_props},
        max_items=max_nodes,
    )
    rows = response.get("data", [])
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "apps/<id>/nodes",
            "selector": selector,
            "included_props": selected_props.split(","),
            "node_count": len(rows),
        }
    )
    return {
        "app": selector,
        "meta": meta,
        "data": rows,
    }


async def count_app_nodes(
    app: str,
) -> dict[str, Any]:
    selector = app.strip()
    if not selector:
        raise ValueError("app must not be empty")

    response = await collector_get(
        f"/apps/{quote(selector, safe='')}/nodes",
        params={"props": "nodename", "limit": 1, "offset": 0},
    )
    meta = response.get("meta", {})
    return {
        "app": selector,
        "count": meta.get("total", len(response.get("data", []))),
        "meta": {
            "source": "apps/<id>/nodes",
            "selector": selector,
            "raw_meta": meta,
        },
    }


async def count_apps(
    filters: dict[str, str] | str | None = None,
    search: str | None = None,
) -> dict[str, Any]:
    parsed_filters = parse_collector_filters(filters)
    response = await collector_get(
        "/apps",
        params=collection_params(
            filters=parsed_filters,
            props="app",
            orderby=None,
            search=search,
            limit=1,
            offset=0,
        ),
    )
    meta = response.get("meta", {})
    return {
        "count": meta.get("total", len(response.get("data", []))),
        "filters": {field: value for field, value in parsed_filters},
        "search": search,
    }


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

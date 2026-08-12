from typing import Any

from opensvc_collector_mcp.client import collector_get, collector_get_page
from opensvc_collector_mcp.core.utils import collection_params, parse_collector_filters

from ._common import quote_app_selector, require_app_selector


async def get_app_relation_page(
    *,
    app: str,
    relation: str,
    filters: dict[str, str] | str | None,
    props: str,
    orderby: str | None,
    search: str | None,
    limit: int,
    offset: int,
) -> dict[str, Any]:
    selector = require_app_selector(app)
    response = await collector_get_page(
        f"/apps/{quote_app_selector(selector)}/{relation}",
        params=collection_params(
            filters=parse_collector_filters(filters),
            props=props,
            orderby=orderby,
            search=search,
            limit=limit,
            offset=offset,
        ),
    )
    return {"app": selector, **response}


async def count_app_relation(
    *,
    app: str,
    relation: str,
    props: str,
) -> dict[str, Any]:
    selector = require_app_selector(app)
    response = await collector_get(
        f"/apps/{quote_app_selector(selector)}/{relation}",
        params={"props": props, "limit": 1, "offset": 0},
    )
    meta = response.get("meta", {})
    return {
        "app": selector,
        "count": meta.get("total", len(response.get("data", []))),
        "meta": {
            "source": f"apps/<id>/{relation}",
            "selector": selector,
            "raw_meta": meta,
        },
    }

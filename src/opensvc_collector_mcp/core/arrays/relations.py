from typing import Any

from opensvc_collector_mcp.client import collector_get_page
from opensvc_collector_mcp.core.collection import collection_params, parse_collector_filters

from ._common import quote_selector, require_selector


DEFAULT_ARRAY_PROXY_PROPS = "id,array_id,node_id"
DEFAULT_ARRAY_TARGET_PROPS = "id,array_id,array_tgtid"


async def get_array_proxies(
    array: str,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "id",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    return await _get_array_relation(
        array=array,
        relation="proxies",
        filters=filters,
        props=props or DEFAULT_ARRAY_PROXY_PROPS,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )


async def get_array_targets(
    array: str,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "id",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    return await _get_array_relation(
        array=array,
        relation="targets",
        filters=filters,
        props=props or DEFAULT_ARRAY_TARGET_PROPS,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )


async def _get_array_relation(
    *,
    array: str,
    relation: str,
    filters: dict[str, str] | str | None,
    props: str,
    orderby: str | None,
    search: str | None,
    limit: int,
    offset: int,
) -> dict[str, Any]:
    selector = require_selector(array, "array")
    response = await collector_get_page(
        f"/arrays/{quote_selector(selector)}/{relation}",
        params=collection_params(
            filters=parse_collector_filters(filters),
            props=props,
            orderby=orderby,
            search=search,
            limit=limit,
            offset=offset,
        ),
    )
    return {"array": selector, **response}

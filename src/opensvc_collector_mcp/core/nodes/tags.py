from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get_page
from opensvc_collector_mcp.core.collection import collection_params, parse_collector_filters


async def get_node_tags(
    nodename: str,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "tag_name",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    nodename = nodename.strip()
    if not nodename:
        raise ValueError("nodename must not be empty")

    parsed_filters = parse_collector_filters(filters)
    response = await collector_get_page(
        f"/nodes/{quote(nodename, safe='')}/tags",
        params=collection_params(
            filters=parsed_filters,
            props=props,
            orderby=orderby,
            search=search,
            limit=limit,
            offset=offset,
        ),
    )
    return {"nodename": nodename, **response}

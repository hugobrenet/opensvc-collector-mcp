from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get
from opensvc_collector_mcp.core.utils import collection_params, parse_collector_filters


async def get_node_checks(
    nodename: str,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "chk_type",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    nodename = nodename.strip()
    if not nodename:
        raise ValueError("nodename must not be empty")

    parsed_filters = parse_collector_filters(filters)
    response = await collector_get(
        f"/nodes/{quote(nodename, safe='')}/checks",
        params=collection_params(
            filters=parsed_filters,
            props=props,
            orderby=orderby,
            search=search,
            limit=limit,
            offset=offset,
        ),
    )
    meta = dict(response.get("meta", {}))
    meta.update({"source": "node_checks", "filter": {"nodename": nodename, **{k: v for k, v in parsed_filters}}, "output_count": len(response.get("data", []))})
    return {"nodename": nodename, "meta": meta, "data": response.get("data", [])}

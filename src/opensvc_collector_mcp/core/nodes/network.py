from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get_page
from opensvc_collector_mcp.core.collection import collection_params, parse_collector_filters


NODE_NETWORK_PROPS = (
    "mac,net_team_responsible,intf,addr,prio,net_gateway,net_comment,"
    "net_end,net_netmask,mask,net_network,addr_type,net_broadcast,"
    "net_pvid,net_begin,flag_deprecated,addr_updated,net_id,net_name"
)


async def get_node_network(
    nodename: str,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "intf",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    nodename = nodename.strip()
    if not nodename:
        raise ValueError("nodename must not be empty")

    selected_props = props or NODE_NETWORK_PROPS
    parsed_filters = parse_collector_filters(filters)
    response = await collector_get_page(
        f"/nodes/{quote(nodename, safe='')}/ips",
        params=collection_params(
            filters=parsed_filters,
            props=selected_props,
            orderby=orderby,
            search=search,
            limit=limit,
            offset=offset,
        ),
    )
    return {"nodename": nodename, **response}

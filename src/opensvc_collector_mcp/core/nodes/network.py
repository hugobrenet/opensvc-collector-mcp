from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get_all


NODE_NETWORK_PROPS = (
    "mac,net_team_responsible,intf,addr,prio,net_gateway,net_comment,"
    "net_end,net_netmask,mask,net_network,addr_type,net_broadcast,"
    "net_pvid,net_begin,flag_deprecated,addr_updated,net_id,net_name"
)


async def get_node_network(nodename: str) -> dict[str, Any]:
    nodename = nodename.strip()
    if not nodename:
        raise ValueError("nodename must not be empty")

    response = await collector_get_all(
        f"/nodes/{quote(nodename, safe='')}/ips",
        params={"props": NODE_NETWORK_PROPS},
        strategy="paged",
    )
    return {
        "nodename": nodename,
        "meta": response.get("meta", {}),
        "data": response.get("data", []),
    }

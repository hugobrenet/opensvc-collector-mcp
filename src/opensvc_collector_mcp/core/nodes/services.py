from typing import Any

from opensvc_collector_mcp.client import collector_get


NODE_SERVICES_INSTANCE_PROPS = (
    "services.svcname:svcname,services.svc_status:svc_status,"
    "services.svc_env:svc_env,services.svc_app:svc_app,"
    "services.svc_topology:svc_topology,svcmon.mon_vmname:mon_vmname,"
    "svcmon.mon_availstatus:mon_availstatus,nodes.nodename:nodename"
)


async def get_node_services(
    nodename: str,
    page_size: int = 1000,
    max_instances: int = 100000,
) -> dict[str, Any]:
    nodename = nodename.strip()
    if not nodename:
        raise ValueError("nodename must not be empty")

    page_size = max(1, min(page_size, 5000))
    max_instances = max(1, min(max_instances, 500000))
    matches: list[dict[str, Any]] = []
    scanned = 0
    offset = 0
    total: int | None = None

    while scanned < max_instances:
        response = await collector_get(
            "/services_instances",
            params=[
                ("props", NODE_SERVICES_INSTANCE_PROPS),
                ("filters", f"nodes.nodename={nodename}"),
                ("limit", min(page_size, max_instances - scanned)),
                ("offset", offset),
            ],
        )
        meta = response.get("meta", {})
        data = response.get("data", [])
        if total is None:
            total = meta.get("total")

        matches.extend(data)

        count = len(data)
        scanned += count
        offset += count
        if count == 0 or count < page_size:
            break

    complete = total is None or scanned >= total
    return {
        "nodename": nodename,
        "meta": {
            "count": len(matches),
            "total": len(matches) if complete else None,
            "scanned": scanned,
            "collector_total": total,
            "complete": complete,
            "page_size": page_size,
            "max_instances": max_instances,
            "source": "services_instances",
            "filter": {"nodes.nodename": nodename},
            "included_props": NODE_SERVICES_INSTANCE_PROPS.split(","),
        },
        "data": matches,
    }

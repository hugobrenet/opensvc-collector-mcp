from typing import Any

from opensvc_collector_mcp.client import collector_get
from opensvc_collector_mcp.core.utils import collection_params, parse_collector_filters


NODE_SERVICES_INSTANCE_PROPS = (
    "services.svcname:svcname,services.svc_status:svc_status,"
    "services.svc_env:svc_env,services.svc_app:svc_app,"
    "services.svc_topology:svc_topology,svcmon.mon_vmname:mon_vmname,"
    "svcmon.mon_availstatus:mon_availstatus,nodes.nodename:nodename"
)


async def get_node_services(
    nodename: str,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "services.svcname",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    nodename = nodename.strip()
    if not nodename:
        raise ValueError("nodename must not be empty")

    selected_props = props or NODE_SERVICES_INSTANCE_PROPS
    parsed_filters = [("nodes.nodename", nodename), *parse_collector_filters(filters)]
    response = await collector_get(
        "/services_instances",
        params=collection_params(
            filters=parsed_filters,
            props=selected_props,
            orderby=orderby,
            search=search,
            limit=limit,
            offset=offset,
        ),
    )
    rows = response.get("data", [])
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "services_instances",
            "filter": {field: value for field, value in parsed_filters},
            "included_props": selected_props.split(","),
            "output_count": len(rows),
        }
    )
    return {"nodename": nodename, "meta": meta, "data": rows}

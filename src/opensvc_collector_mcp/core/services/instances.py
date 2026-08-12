from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get_page
from opensvc_collector_mcp.core.collection import collection_params

from ._common import _parse_service_filters


SERVICE_INSTANCES_PROPS = (
    "services.svcname:svcname,services.svc_status:svc_status,"
    "services.svc_env:svc_env,services.svc_app:svc_app,"
    "services.svc_availstatus:svc_availstatus,"
    "services.svc_topology:svc_topology,nodes.nodename:nodename,"
    "svcmon.mon_vmname:mon_vmname,svcmon.mon_availstatus:mon_availstatus,"
    "svcmon.mon_frozen:mon_frozen,svcmon.mon_frozen_at:mon_frozen_at,"
    "svcmon.mon_encap_frozen_at:mon_encap_frozen_at"
)
SERVICE_NODES_PROPS = (
    "nodes.nodename:nodename,svcmon.node_id:node_id,svcmon.id:id,"
    "svcmon.svc_id:svc_id,svcmon.mon_vmname:mon_vmname,"
    "svcmon.mon_overallstatus:mon_overallstatus,"
    "svcmon.mon_availstatus:mon_availstatus,svcmon.mon_frozen:mon_frozen,"
    "svcmon.mon_frozen_at:mon_frozen_at,"
    "svcmon.mon_encap_frozen_at:mon_encap_frozen_at,"
    "svcmon.mon_updated:mon_updated,svcmon.mon_changed:mon_changed"
)


async def get_service_instances(
    svcname: str,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "nodes.nodename",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    selected_props = props or SERVICE_INSTANCES_PROPS
    parsed_filters = _service_instance_filters(
        [("svcname", svcname), *_parse_service_filters(filters)]
    )
    response = await collector_get_page(
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
    return {"svcname": svcname, **response}


async def get_service_nodes(
    svcname: str,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "nodes.nodename",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    selected_props = props or SERVICE_NODES_PROPS
    parsed_filters = _parse_service_filters(filters)
    response = await collector_get_page(
        f"/services/{quote(svcname, safe='')}/nodes",
        params=collection_params(
            filters=parsed_filters,
            props=selected_props,
            orderby=orderby,
            search=search,
            limit=limit,
            offset=offset,
        ),
    )
    return {"svcname": svcname, **response}


def _service_instance_filters(filters: list[tuple[str, str]]) -> list[tuple[str, str]]:
    return [(_service_instance_filter_field(field), value) for field, value in filters]


def _service_instance_filter_field(field: str) -> str:
    if "." in field:
        return field
    return f"services.{field}"

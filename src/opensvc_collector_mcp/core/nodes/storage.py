from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get_page
from opensvc_collector_mcp.core.utils import collection_params, parse_collector_filters


NODE_DISKS_PROPS = (
    "svcdisks.id:id,svcdisks.node_id:node_id,svcdisks.svc_id:svc_id,"
    "svcdisks.app_id:app_id,svcdisks.disk_id:disk_id,"
    "svcdisks.disk_size:disk_size,svcdisks.disk_used:disk_used,"
    "svcdisks.disk_local:disk_local,svcdisks.disk_dg:disk_dg,"
    "svcdisks.disk_vendor:disk_vendor,svcdisks.disk_model:disk_model,"
    "svcdisks.disk_region:disk_region,svcdisks.disk_updated:disk_updated,"
    "diskinfo.id:diskinfo_id,diskinfo.disk_id:diskinfo_disk_id,"
    "diskinfo.disk_name:disk_name,diskinfo.disk_devid:disk_devid,"
    "diskinfo.disk_alloc:disk_alloc,diskinfo.disk_level:disk_level,"
    "diskinfo.disk_raid:disk_raid,diskinfo.disk_group:disk_group,"
    "diskinfo.disk_arrayid:disk_arrayid,"
    "diskinfo.disk_controller:disk_controller,"
    "diskinfo.disk_created:disk_created,"
    "diskinfo.disk_updated:diskinfo_updated,"
    "stor_array.id:array_id,stor_array.array_name:array_name,"
    "stor_array.array_model:array_model,"
    "stor_array.array_firmware:array_firmware"
)

NODE_DISK_PROP_ALIASES = {
    "id": "svcdisks.id:id",
    "node_id": "svcdisks.node_id:node_id",
    "svc_id": "svcdisks.svc_id:svc_id",
    "app_id": "svcdisks.app_id:app_id",
    "disk_id": "svcdisks.disk_id:disk_id",
    "disk_size": "svcdisks.disk_size:disk_size",
    "disk_used": "svcdisks.disk_used:disk_used",
    "disk_local": "svcdisks.disk_local:disk_local",
    "disk_dg": "svcdisks.disk_dg:disk_dg",
    "disk_vendor": "svcdisks.disk_vendor:disk_vendor",
    "disk_model": "svcdisks.disk_model:disk_model",
    "disk_region": "svcdisks.disk_region:disk_region",
    "disk_updated": "svcdisks.disk_updated:disk_updated",
    "diskinfo_id": "diskinfo.id:diskinfo_id",
    "diskinfo_disk_id": "diskinfo.disk_id:diskinfo_disk_id",
    "disk_name": "diskinfo.disk_name:disk_name",
    "disk_devid": "diskinfo.disk_devid:disk_devid",
    "disk_alloc": "diskinfo.disk_alloc:disk_alloc",
    "disk_level": "diskinfo.disk_level:disk_level",
    "disk_raid": "diskinfo.disk_raid:disk_raid",
    "disk_group": "diskinfo.disk_group:disk_group",
    "disk_arrayid": "diskinfo.disk_arrayid:disk_arrayid",
    "disk_controller": "diskinfo.disk_controller:disk_controller",
    "disk_created": "diskinfo.disk_created:disk_created",
    "diskinfo_updated": "diskinfo.disk_updated:diskinfo_updated",
    "array_id": "stor_array.id:array_id",
    "array_name": "stor_array.array_name:array_name",
    "array_model": "stor_array.array_model:array_model",
    "array_firmware": "stor_array.array_firmware:array_firmware",
}


def _normalize_node_disk_props(props: str | None) -> str:
    if not props:
        return NODE_DISKS_PROPS

    normalized: list[str] = []
    for raw_prop in props.split(","):
        prop = raw_prop.strip()
        if not prop:
            continue
        normalized.append(NODE_DISK_PROP_ALIASES.get(prop, prop))
    return ",".join(normalized)


async def get_node_disks(
    nodename: str,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    nodename = nodename.strip()
    if not nodename:
        raise ValueError("nodename must not be empty")

    parsed_filters = parse_collector_filters(filters)
    selected_props = _normalize_node_disk_props(props)
    response = await collector_get_page(
        f"/nodes/{quote(nodename, safe='')}/disks",
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

from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get_all

from ._common import _parse_service_filters


SERVICE_HBAS_PROPS = (
    "nodes.nodename:nodename,node_hba.node_id:node_id,"
    "node_hba.id:id,node_hba.hba_id:hba_id,"
    "node_hba.hba_type:hba_type,node_hba.updated:updated"
)
SERVICE_TARGETS_PROPS = (
    "nodes.nodename:nodename,stor_zone.node_id:node_id,"
    "stor_zone.id:id,stor_zone.hba_id:hba_id,stor_zone.tgt_id:tgt_id,"
    "stor_zone.updated:updated,stor_array.id:array_id,"
    "stor_array.array_name:array_name,stor_array.array_model:array_model,"
    "stor_array.array_firmware:array_firmware,"
    "stor_array.array_comment:array_comment"
)
SERVICE_DISKS_PROPS = (
    "nodes.nodename:nodename,svcdisks.node_id:node_id,"
    "svcdisks.id:id,svcdisks.svc_id:svc_id,svcdisks.disk_id:disk_id,"
    "svcdisks.disk_size:disk_size,svcdisks.disk_used:disk_used,"
    "svcdisks.disk_local:disk_local,svcdisks.disk_vendor:disk_vendor,"
    "svcdisks.disk_model:disk_model,svcdisks.disk_dg:disk_dg,"
    "svcdisks.disk_region:disk_region,svcdisks.disk_updated:disk_updated,"
    "diskinfo.disk_name:disk_name,diskinfo.disk_devid:disk_devid,"
    "diskinfo.disk_alloc:disk_alloc,diskinfo.disk_raid:disk_raid,"
    "diskinfo.disk_group:disk_group,diskinfo.disk_arrayid:disk_arrayid,"
    "stor_array.array_name:array_name,stor_array.array_model:array_model"
)


async def get_service_hbas(
    svcname: str,
    props: str | None = None,
    page_size: int = 1000,
    max_hbas: int = 10000,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    selected_props = props or SERVICE_HBAS_PROPS
    response = await collector_get_all(
        f"/services/{quote(svcname, safe='')}/hbas",
        params={"props": selected_props},
        strategy="paged",
        page_size=page_size,
        max_items=max_hbas,
    )
    rows = response.get("data", [])
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "service_hbas",
            "filter": {"svcname": svcname},
            "included_props": selected_props.split(","),
            "hba_count": len(rows),
        }
    )
    return {
        "svcname": svcname,
        "meta": meta,
        "data": rows,
    }


async def get_service_targets(
    svcname: str,
    filters: dict[str, str] | str | None = None,
    hba_id: str | None = None,
    node_id: str | None = None,
    tgt_id: str | None = None,
    array_name: str | None = None,
    props: str | None = None,
    page_size: int = 1000,
    max_targets: int = 10000,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    selected_props = props or SERVICE_TARGETS_PROPS
    parsed_filters = _service_target_filters(
        filters,
        hba_id=hba_id,
        node_id=node_id,
        tgt_id=tgt_id,
        array_name=array_name,
    )
    response = await collector_get_all(
        f"/services/{quote(svcname, safe='')}/targets",
        params=_service_target_params(
            filters=parsed_filters,
            props=selected_props,
        ),
        strategy="paged",
        page_size=page_size,
        max_items=max_targets,
    )
    rows = response.get("data", [])
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "service_targets",
            "filter": {
                "svcname": svcname,
                **{field: value for field, value in parsed_filters},
            },
            "included_props": selected_props.split(","),
            "target_count": len(rows),
        }
    )
    return {
        "svcname": svcname,
        "meta": meta,
        "data": rows,
    }


async def get_service_disks(
    svcname: str,
    props: str | None = None,
    page_size: int = 1000,
    max_disks: int = 10000,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    selected_props = props or SERVICE_DISKS_PROPS
    response = await collector_get_all(
        f"/services/{quote(svcname, safe='')}/disks",
        params={"props": selected_props},
        strategy="paged",
        page_size=page_size,
        max_items=max_disks,
    )
    rows = response.get("data", [])
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "service_disks",
            "filter": {"svcname": svcname},
            "included_props": selected_props.split(","),
            "disk_count": len(rows),
        }
    )
    return {
        "svcname": svcname,
        "meta": meta,
        "data": rows,
    }


def _service_target_filters(
    raw_filters: dict[str, str] | str | None = None,
    **criteria: str | None,
) -> list[tuple[str, str]]:
    filters = [
        (_service_target_filter_field(field), value)
        for field, value in _parse_service_filters(raw_filters)
    ]
    for field, value in criteria.items():
        if value is None:
            continue
        value = value.strip()
        if value:
            filters.append((_service_target_filter_field(field), value))
    return filters


def _service_target_filter_field(field: str) -> str:
    if "." in field:
        return field
    return {
        "id": "stor_zone.id",
        "node_id": "stor_zone.node_id",
        "hba_id": "stor_zone.hba_id",
        "tgt_id": "stor_zone.tgt_id",
        "updated": "stor_zone.updated",
        "array_id": "stor_array.id",
        "array_name": "stor_array.array_name",
        "array_model": "stor_array.array_model",
        "array_firmware": "stor_array.array_firmware",
        "array_comment": "stor_array.array_comment",
    }.get(field, field)


def _service_target_params(
    filters: list[tuple[str, str]],
    props: str,
) -> list[tuple[str, Any]]:
    params: list[tuple[str, Any]] = [("props", props)]
    for field, value in filters:
        params.append(("filters", f"{field}={value}"))
    return params

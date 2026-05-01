from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get, collector_get_all
from opensvc_collector_mcp.core.utils import (
    collection_params,
    enrich_rows_with_nodenames,
    get_nodenames_by_node_ids,
)

from ._common import _parse_service_filters, _unresolved_node_ids


SERVICE_RESOURCES_PROPS = "nodes.nodename:nodename,rid,res_key,res_value,updated"
SERVICE_RESOURCE_STATUS_PROPS = (
    "node_id,rid,vmname,res_type,res_status,res_desc,res_disable,"
    "res_optional,res_monitor,changed,updated"
)


async def get_service_resources(
    svcname: str,
    page_size: int = 1000,
    max_items: int = 200000,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    response = await collector_get_all(
        f"/services/{quote(svcname, safe='')}/resinfo",
        params={"props": SERVICE_RESOURCES_PROPS},
        page_size=page_size,
        max_items=max_items,
    )
    rows = response.get("data", [])
    resources = _group_service_resources(rows)
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "services_resinfo",
            "filter": {"svcname": svcname},
            "included_props": SERVICE_RESOURCES_PROPS.split(","),
            "raw_count": len(rows),
            "resource_count": len(resources),
        }
    )
    return {
        "svcname": svcname,
        "meta": meta,
        "resources": resources,
    }


async def get_service_resource_status(
    svcname: str,
    filters: dict[str, str] | str | None = None,
    rid: str | None = None,
    node_id: str | None = None,
    vmname: str | None = None,
    res_type: str | None = None,
    res_status: str | None = None,
    res_disable: str | None = None,
    res_optional: str | None = None,
    res_monitor: str | None = None,
    props: str | None = None,
    orderby: str | None = "rid",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    selected_props = props or SERVICE_RESOURCE_STATUS_PROPS
    parsed_filters = _service_resource_status_filters(
        filters,
        rid=rid,
        node_id=node_id,
        vmname=vmname,
        res_type=res_type,
        res_status=res_status,
        res_disable=res_disable,
        res_optional=res_optional,
        res_monitor=res_monitor,
    )
    response = await collector_get(
        f"/services/{quote(svcname, safe='')}/resources",
        params=_service_resource_status_params(
            filters=parsed_filters,
            props=selected_props,
            orderby=orderby,
            search=search,
            limit=limit,
            offset=offset,
        ),
    )
    raw_rows = response.get("data", [])
    nodenames_by_node_id = await get_nodenames_by_node_ids(
        str(row.get("node_id") or "") for row in raw_rows
    )
    rows = enrich_rows_with_nodenames(raw_rows, nodenames_by_node_id)
    unresolved_node_ids = _unresolved_node_ids(rows, nodenames_by_node_id)
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "service_resource_status",
            "filter": {
                "svcname": svcname,
                **{field: value for field, value in parsed_filters},
            },
            "included_props": selected_props.split(","),
            "resource_count": len(rows),
            "output_count": len(rows),
            "node_names_resolved": not unresolved_node_ids,
            "node_name_count": len(nodenames_by_node_id),
            "unresolved_node_ids": unresolved_node_ids,
        }
    )
    return {
        "svcname": svcname,
        "meta": meta,
        "data": rows,
    }


def _group_service_resources(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        rid = str(row.get("rid") or "")
        nodename = str(row.get("nodename") or "")
        if not rid:
            continue

        key = (rid, nodename)
        resource = grouped.setdefault(
            key,
            {
                "rid": rid,
                "resource_type": _resource_type_from_rid(rid),
                "properties": {},
            },
        )
        if nodename:
            resource["nodename"] = nodename

        updated = row.get("updated")
        if updated and (
            not resource.get("updated") or str(updated) > str(resource["updated"])
        ):
            resource["updated"] = updated

        res_key = row.get("res_key")
        if not res_key:
            continue
        res_key = str(res_key)
        res_value = row.get("res_value")
        resource["properties"][res_key] = res_value
        if res_key in {
            "driver",
            "name",
            "monitor",
            "optional",
            "disabled",
            "shared",
            "encap",
            "standby",
            "tags",
        }:
            resource[res_key] = res_value

    return sorted(
        grouped.values(),
        key=lambda resource: (
            str(resource.get("resource_type") or ""),
            str(resource.get("rid") or ""),
            str(resource.get("nodename") or ""),
        ),
    )


def _resource_type_from_rid(rid: str) -> str:
    return rid.split("#", 1)[0] if "#" in rid else rid


def _service_resource_status_filters(
    raw_filters: dict[str, str] | str | None = None,
    **criteria: str | None,
) -> list[tuple[str, str]]:
    filters = [
        (_service_resource_status_filter_field(field), value)
        for field, value in _parse_service_filters(raw_filters)
    ]
    for field, value in criteria.items():
        if value is None:
            continue
        value = value.strip()
        if value:
            filters.append((_service_resource_status_filter_field(field), value))
    return filters


def _service_resource_status_filter_field(field: str) -> str:
    if "." in field:
        return field
    return {
        "id": "resmon.id",
        "svc_id": "resmon.svc_id",
        "node_id": "resmon.node_id",
        "rid": "resmon.rid",
        "vmname": "resmon.vmname",
        "res_type": "resmon.res_type",
        "res_status": "resmon.res_status",
        "res_desc": "resmon.res_desc",
        "res_log": "resmon.res_log",
        "res_disable": "resmon.res_disable",
        "res_optional": "resmon.res_optional",
        "res_monitor": "resmon.res_monitor",
        "changed": "resmon.changed",
        "updated": "resmon.updated",
    }.get(field, field)


def _service_resource_status_params(
    filters: list[tuple[str, str]],
    props: str,
    orderby: str | None,
    search: str | None,
    limit: int,
    offset: int,
) -> list[tuple[str, Any]]:
    return collection_params(
        filters=filters,
        props=props,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )

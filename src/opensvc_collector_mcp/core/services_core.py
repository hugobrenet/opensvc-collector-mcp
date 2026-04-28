from configparser import ConfigParser, Error as ConfigParserError
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import quote

import httpx

from opensvc_collector_mcp.client import collector_get, collector_get_all


DEFAULT_LIST_SERVICE_PROPS = (
    "svcname,svc_app,svc_env,svc_status,svc_availstatus,svc_topology,"
    "svc_nodes,svc_drpnodes,svc_frozen,svc_ha,svc_created,updated"
)
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
SERVICE_HBAS_PROPS = (
    "nodes.nodename:nodename,node_hba.node_id:node_id,"
    "node_hba.id:id,node_hba.hba_id:hba_id,"
    "node_hba.hba_type:hba_type,node_hba.updated:updated"
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
SERVICE_RESOURCES_PROPS = (
    "nodes.nodename:nodename,rid,res_key,res_value,updated"
)
SERVICE_CONFIG_PROPS = "svcname,svc_config,svc_config_updated,updated"
SERVICE_ALERTS_PROPS = (
    "alert,dashboard.dash_type,dashboard.dash_severity,dashboard.dash_created,"
    "dashboard.dash_updated,dashboard.node_id,dashboard.id,"
    "dashboard.dash_env,dashboard.dash_instance"
)
SERVICE_CHECKS_PROPS = (
    "checks_live.chk_type,checks_live.chk_instance,checks_live.chk_value,"
    "checks_live.chk_err,checks_live.chk_low,checks_live.chk_high,"
    "checks_live.chk_threshold_provider,checks_live.chk_created,"
    "checks_live.chk_updated,checks_live.node_id,checks_live.id"
)
SERVICE_TAGS_PROPS = (
    "tags.tag_name,tags.tag_id,tags.tag_data,tags.tag_exclude,"
    "tags.tag_created"
)
TAG_LOOKUP_PROPS = "tag_name,tag_id,tag_data,tag_exclude,tag_created"
SERVICE_ACTIONS_PROPS = (
    "action,status,begin,end,time,ack,acked_by,acked_date,acked_comment,"
    "rid,subset,hostid,node_id"
)
SERVICE_ACTIONS_LOG_PROP = "status_log"
FROZEN_SERVICES_PROPS = (
    "services.svcname:svcname,services.svc_status:svc_status,"
    "services.svc_availstatus:svc_availstatus,services.svc_frozen:svc_frozen,"
    "services.svc_env:svc_env,services.svc_app:svc_app,"
    "services.svc_topology:svc_topology,nodes.nodename:nodename,"
    "svcmon.mon_vmname:mon_vmname,svcmon.mon_availstatus:mon_availstatus,"
    "svcmon.mon_frozen:mon_frozen,svcmon.mon_frozen_at:mon_frozen_at,"
    "svcmon.mon_encap_frozen_at:mon_encap_frozen_at"
)


async def list_services(props: str | None = None) -> dict[str, Any]:
    selected_props = props or DEFAULT_LIST_SERVICE_PROPS
    return await collector_get_all(
        "/services",
        params={"props": selected_props},
        strategy="paged",
    )


async def search_services(
    filters: dict[str, str] | str | None = None,
    svcname: str | None = None,
    svc_app: str | None = None,
    svc_env: str | None = None,
    svc_status: str | None = None,
    svc_availstatus: str | None = None,
    svc_topology: str | None = None,
    svc_frozen: str | None = None,
    props: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    selected_props = props or DEFAULT_LIST_SERVICE_PROPS
    parsed_filters = _service_search_filters(
        filters,
        svcname=svcname,
        svc_app=svc_app,
        svc_env=svc_env,
        svc_status=svc_status,
        svc_availstatus=svc_availstatus,
        svc_topology=svc_topology,
        svc_frozen=svc_frozen,
    )
    return await collector_get(
        "/services",
        params=_service_search_params(
            filters=parsed_filters,
            props=selected_props,
            limit=limit,
            offset=offset,
        ),
    )


async def count_services(
    filters: dict[str, str] | str | None = None,
    svcname: str | None = None,
    svc_app: str | None = None,
    svc_env: str | None = None,
    svc_status: str | None = None,
    svc_availstatus: str | None = None,
    svc_topology: str | None = None,
    svc_frozen: str | None = None,
) -> dict[str, Any]:
    parsed_filters = _service_search_filters(
        filters,
        svcname=svcname,
        svc_app=svc_app,
        svc_env=svc_env,
        svc_status=svc_status,
        svc_availstatus=svc_availstatus,
        svc_topology=svc_topology,
        svc_frozen=svc_frozen,
    )
    response = await collector_get(
        "/services",
        params=_service_search_params(
            filters=parsed_filters,
            props="svcname",
            limit=1,
            offset=0,
        ),
    )
    meta = response.get("meta", {})
    return {
        "count": meta.get("total"),
        "filters": {field: value for field, value in parsed_filters},
    }


async def get_service(svcname: str) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    return await collector_get(f"/services/{quote(svcname, safe='')}")


async def get_service_config(
    svcname: str,
    include_raw_config: bool = True,
    include_sections: bool = True,
    raw_config_max_chars: int = 20000,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    raw_config_max_chars = max(0, min(raw_config_max_chars, 100000))
    response = await collector_get(
        f"/services/{quote(svcname, safe='')}",
        params={"props": SERVICE_CONFIG_PROPS},
    )
    rows = response.get("data", [])
    row = rows[0] if rows else {}
    raw_config = row.get("svc_config")
    config_text = raw_config if isinstance(raw_config, str) else ""
    config = _truncate_text(config_text, raw_config_max_chars) if include_raw_config else None
    sections = _parse_service_config_sections(config_text) if include_sections else []
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "service_config",
            "filter": {"svcname": svcname},
            "included_props": SERVICE_CONFIG_PROPS.split(","),
            "config_present": bool(config_text),
            "config_length": len(config_text),
            "config_line_count": len(config_text.splitlines()) if config_text else 0,
            "section_count": len(sections),
            "include_raw_config": include_raw_config,
            "include_sections": include_sections,
            "raw_config_max_chars": raw_config_max_chars,
            "raw_config_truncated": bool(
                include_raw_config and len(config_text) > raw_config_max_chars
            ),
        }
    )
    return {
        "svcname": svcname,
        "meta": meta,
        "config_updated": row.get("svc_config_updated"),
        "updated": row.get("updated"),
        "config": config,
        "sections": sections,
    }


async def get_service_instances(
    svcname: str,
    page_size: int = 1000,
    max_instances: int = 100000,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    response = await collector_get_all(
        "/services_instances",
        params=[
            ("props", SERVICE_INSTANCES_PROPS),
            ("filters", f"services.svcname={svcname}"),
        ],
        strategy="paged",
        page_size=page_size,
        max_items=max_instances,
    )
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "services_instances",
            "filter": {"services.svcname": svcname},
            "included_props": SERVICE_INSTANCES_PROPS.split(","),
        }
    )
    return {
        "svcname": svcname,
        "meta": meta,
        "data": response.get("data", []),
    }


async def get_service_nodes(
    svcname: str,
    props: str | None = None,
    page_size: int = 1000,
    max_nodes: int = 10000,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    selected_props = props or SERVICE_NODES_PROPS
    response = await collector_get_all(
        f"/services/{quote(svcname, safe='')}/nodes",
        params={"props": selected_props},
        strategy="paged",
        page_size=page_size,
        max_items=max_nodes,
    )
    rows = response.get("data", [])
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "service_nodes",
            "filter": {"svcname": svcname},
            "included_props": selected_props.split(","),
            "node_count": len(rows),
        }
    )
    return {
        "svcname": svcname,
        "meta": meta,
        "data": rows,
    }


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
        strategy="paged",
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


async def search_services_by_tag(
    tag_name: str,
    props: str | None = None,
    page_size: int = 1000,
    max_services: int = 200000,
) -> dict[str, Any]:
    tag_name = tag_name.strip()
    if not tag_name:
        raise ValueError("tag_name must not be empty")

    tag = await _resolve_tag_by_name(tag_name)
    if not tag:
        return {
            "tag_name": tag_name,
            "tag_id": None,
            "meta": {
                "count": 0,
                "source": "tags",
                "complete": True,
                "raw_count": 0,
                "service_count": 0,
                "duplicate_count": 0,
            },
            "data": [],
        }

    tag_id = str(tag.get("tag_id") or "")
    if not tag_id:
        return {
            "tag_name": tag_name,
            "tag_id": None,
            "meta": {
                "count": 0,
                "source": "tags",
                "complete": True,
                "raw_count": 0,
                "service_count": 0,
                "duplicate_count": 0,
            },
            "data": [],
        }

    selected_props = _ensure_props_include(props or DEFAULT_LIST_SERVICE_PROPS, "svcname")
    response = await collector_get_all(
        f"/tags/{quote(tag_id, safe='')}/services",
        params={"props": selected_props},
        strategy="paged",
        page_size=page_size,
        max_items=max_services,
    )
    raw_rows = response.get("data", [])
    rows = _dedupe_service_rows_by_name(raw_rows)
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "tags/<tag_id>/services",
            "filter": {"tag_name": tag_name, "tag_id": tag_id},
            "included_props": selected_props.split(","),
            "raw_count": len(raw_rows),
            "service_count": len(rows),
            "duplicate_count": len(raw_rows) - len(rows),
        }
    )
    return {
        "tag_name": tag_name,
        "tag_id": tag_id,
        "tag": tag,
        "meta": meta,
        "data": rows,
    }


async def search_services_without_tag(
    tag_name: str,
    props: str | None = None,
    page_size: int = 1000,
    max_services: int = 200000,
) -> dict[str, Any]:
    tag_name = tag_name.strip()
    if not tag_name:
        raise ValueError("tag_name must not be empty")

    tagged = await search_services_by_tag(
        tag_name=tag_name,
        props="svcname",
        page_size=page_size,
        max_services=max_services,
    )
    tagged_names = {
        str(row.get("svcname")).strip()
        for row in tagged.get("data", [])
        if str(row.get("svcname", "")).strip()
    }

    selected_props = _ensure_props_include(props or DEFAULT_LIST_SERVICE_PROPS, "svcname")
    all_services = await collector_get_all(
        "/services",
        params={"props": selected_props},
        strategy="paged",
        page_size=page_size,
        max_items=max_services,
    )
    all_rows = all_services.get("data", [])
    rows = [
        row
        for row in all_rows
        if str(row.get("svcname", "")).strip() not in tagged_names
    ]
    all_meta = dict(all_services.get("meta", {}))
    complete = bool(all_meta.get("complete")) and bool(tagged.get("meta", {}).get("complete"))
    meta = {
        "count": len(rows),
        "source": "services - tags/<tag_id>/services",
        "filter": {"tag_name": tag_name, "tag_id": tagged.get("tag_id")},
        "included_props": selected_props.split(","),
        "service_count": len(rows),
        "tagged_count": len(tagged_names),
        "tagged_raw_count": tagged.get("meta", {}).get("raw_count"),
        "total_services": all_meta.get("total", len(all_rows)),
        "complete": complete,
        "page_size": all_meta.get("page_size"),
        "max_items": all_meta.get("max_items"),
        "strategy": all_meta.get("strategy"),
    }
    return {
        "tag_name": tag_name,
        "tag_id": tagged.get("tag_id"),
        "tag": tagged.get("tag"),
        "meta": meta,
        "data": rows,
    }


async def get_service_tags(
    svcname: str,
    filters: dict[str, str] | str | None = None,
    tag_name: str | None = None,
    tag_id: str | None = None,
    tag_exclude: str | None = None,
    props: str | None = None,
    page_size: int = 1000,
    max_tags: int = 10000,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    selected_props = props or SERVICE_TAGS_PROPS
    parsed_filters = _service_tag_filters(
        filters,
        tag_name=tag_name,
        tag_id=tag_id,
        tag_exclude=tag_exclude,
    )
    response = await collector_get_all(
        f"/services/{quote(svcname, safe='')}/tags",
        params=_service_tag_params(
            filters=parsed_filters,
            props=selected_props,
        ),
        strategy="paged",
        page_size=page_size,
        max_items=max_tags,
    )
    rows = response.get("data", [])
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "service_tags",
            "filter": {
                "svcname": svcname,
                **{field: value for field, value in parsed_filters},
            },
            "included_props": selected_props.split(","),
            "output_count": len(rows),
        }
    )
    return {
        "svcname": svcname,
        "meta": meta,
        "data": rows,
    }


async def get_service_checks(
    svcname: str,
    filters: dict[str, str] | str | None = None,
    chk_type: str | None = None,
    chk_err: int | str | None = None,
    node_id: str | None = None,
    chk_instance: str | None = None,
    props: str | None = None,
    page_size: int = 1000,
    max_checks: int = 10000,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    selected_props = props or SERVICE_CHECKS_PROPS
    parsed_filters = _service_check_filters(
        filters,
        chk_type=chk_type,
        chk_err=str(chk_err) if chk_err is not None else None,
        node_id=node_id,
        chk_instance=chk_instance,
    )
    response = await collector_get_all(
        f"/services/{quote(svcname, safe='')}/checks",
        params=_service_check_params(
            filters=parsed_filters,
            props=selected_props,
        ),
        strategy="paged",
        page_size=page_size,
        max_items=max_checks,
    )
    rows = response.get("data", [])
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "service_checks",
            "filter": {
                "svcname": svcname,
                **{field: value for field, value in parsed_filters},
            },
            "included_props": selected_props.split(","),
            "output_count": len(rows),
        }
    )
    return {
        "svcname": svcname,
        "meta": meta,
        "data": rows,
    }


async def get_service_alerts(
    svcname: str,
    filters: dict[str, str] | str | None = None,
    dash_type: str | None = None,
    dash_severity: int | str | None = None,
    node_id: str | None = None,
    props: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    selected_props = props or SERVICE_ALERTS_PROPS
    parsed_filters = _service_alert_filters(
        filters,
        dash_type=dash_type,
        dash_severity=str(dash_severity) if dash_severity is not None else None,
        node_id=node_id,
    )
    response = await collector_get(
        f"/services/{quote(svcname, safe='')}/alerts",
        params=_service_alert_params(
            filters=parsed_filters,
            props=selected_props,
            limit=limit,
            offset=offset,
        ),
    )
    rows = response.get("data", [])
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "service_alerts",
            "filter": {
                "svcname": svcname,
                **{field: value for field, value in parsed_filters},
            },
            "included_props": selected_props.split(","),
            "output_count": len(rows),
        }
    )
    return {
        "svcname": svcname,
        "meta": meta,
        "data": rows,
    }


async def get_service_actions(
    svcname: str,
    filters: dict[str, str] | str | None = None,
    action: str | None = None,
    status: str | None = None,
    ack: str | None = None,
    rid: str | None = None,
    subset: str | None = None,
    limit: int = 20,
    offset: int = 0,
    latest: bool = True,
    latest_first: bool = True,
    include_status_log: bool = False,
    include_status_log_preview: bool = True,
    status_log_max_chars: int = 500,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    status_log_max_chars = max(0, min(status_log_max_chars, 5000))
    parsed_filters = _service_action_filters(
        filters,
        action=action,
        status=status,
        ack=ack,
        rid=rid,
        subset=subset,
    )
    endpoint = f"/services/{quote(svcname, safe='')}/actions"
    props = _service_action_props(
        include_status_log=include_status_log,
        include_status_log_preview=include_status_log_preview,
    )

    effective_offset = offset
    total: int | None = None
    if latest:
        probe = await collector_get(
            endpoint,
            params=_service_action_params(
                filters=parsed_filters,
                props="action",
                limit=1,
                offset=0,
            ),
        )
        total = _int_or_none(probe.get("meta", {}).get("total"))
        if total is not None:
            effective_offset = max(0, total - limit)

    response = await collector_get(
        endpoint,
        params=_service_action_params(
            filters=parsed_filters,
            props=props,
            limit=limit,
            offset=effective_offset,
        ),
    )
    meta = dict(response.get("meta", {}))
    if total is None:
        total = _int_or_none(meta.get("total"))
    rows = _service_action_rows(
        response.get("data", []),
        include_status_log=include_status_log,
        include_status_log_preview=include_status_log_preview,
        status_log_max_chars=status_log_max_chars,
        latest_first=latest_first,
    )
    meta.update(
        {
            "source": "service_actions",
            "filter": {
                "svcname": svcname,
                **{field: value for field, value in parsed_filters},
            },
            "requested_latest": latest,
            "latest_first": latest_first,
            "effective_offset": effective_offset,
            "total": total,
            "include_status_log": include_status_log,
            "include_status_log_preview": include_status_log_preview,
            "status_log_max_chars": status_log_max_chars,
            "output_count": len(rows),
        }
    )
    return {
        "svcname": svcname,
        "meta": meta,
        "data": rows,
    }


async def get_service_unacknowledged_errors(
    svcname: str,
    filters: dict[str, str] | str | None = None,
    action: str | None = None,
    rid: str | None = None,
    subset: str | None = None,
    limit: int = 20,
    offset: int = 0,
    latest: bool = True,
    latest_first: bool = True,
    include_status_log: bool = False,
    include_status_log_preview: bool = True,
    status_log_max_chars: int = 500,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    status_log_max_chars = max(0, min(status_log_max_chars, 5000))
    parsed_filters = _service_unacknowledged_error_filters(
        filters,
        action=action,
        rid=rid,
        subset=subset,
    )
    endpoint = f"/services/{quote(svcname, safe='')}/actions_unacknowledged_errors"
    props = _service_action_props(
        include_status_log=include_status_log,
        include_status_log_preview=include_status_log_preview,
    )

    effective_offset = offset
    total: int | None = None
    if latest:
        probe = await collector_get(
            endpoint,
            params=_service_action_params(
                filters=parsed_filters,
                props="action",
                limit=1,
                offset=0,
            ),
        )
        total = _int_or_none(probe.get("meta", {}).get("total"))
        if total is not None:
            effective_offset = max(0, total - limit)

    response = await collector_get(
        endpoint,
        params=_service_action_params(
            filters=parsed_filters,
            props=props,
            limit=limit,
            offset=effective_offset,
        ),
    )
    meta = dict(response.get("meta", {}))
    if total is None:
        total = _int_or_none(meta.get("total"))
    rows = _service_action_rows(
        response.get("data", []),
        include_status_log=include_status_log,
        include_status_log_preview=include_status_log_preview,
        status_log_max_chars=status_log_max_chars,
        latest_first=latest_first,
    )
    meta.update(
        {
            "source": "service_actions_unacknowledged_errors",
            "filter": {
                "svcname": svcname,
                **{field: value for field, value in parsed_filters},
            },
            "implicit_filter": {"status": "err", "ack": "unacknowledged"},
            "requested_latest": latest,
            "latest_first": latest_first,
            "effective_offset": effective_offset,
            "total": total,
            "include_status_log": include_status_log,
            "include_status_log_preview": include_status_log_preview,
            "status_log_max_chars": status_log_max_chars,
            "output_count": len(rows),
        }
    )
    return {
        "svcname": svcname,
        "meta": meta,
        "data": rows,
    }


async def search_frozen_services(
    filters: dict[str, str] | str | None = None,
    min_frozen_days: int = 0,
    page_size: int = 1000,
    max_instances: int = 200000,
) -> dict[str, Any]:
    min_frozen_days = max(0, min(min_frozen_days, 3650))
    parsed_filters = _service_search_filters(filters)
    instance_filters = _service_instance_filters(parsed_filters)
    params: list[tuple[str, Any]] = [
        ("props", FROZEN_SERVICES_PROPS),
        ("filters", "svcmon.mon_frozen=1"),
    ]
    for field, value in instance_filters:
        params.append(("filters", f"{field}={value}"))

    response = await collector_get_all(
        "/services_instances",
        params=params,
        strategy="paged",
        page_size=page_size,
        max_items=max_instances,
    )
    rows = response.get("data", [])
    reference_time = datetime.now().replace(microsecond=0)
    cutoff = reference_time - timedelta(days=min_frozen_days)
    services = _group_frozen_services(
        rows=rows,
        min_frozen_days=min_frozen_days,
        cutoff=cutoff,
        reference_time=reference_time,
    )
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "services_instances",
            "filter": {
                "svcmon.mon_frozen": "1",
                **{field: value for field, value in instance_filters},
            },
            "included_props": FROZEN_SERVICES_PROPS.split(","),
            "raw_count": len(rows),
            "service_count": len(services),
            "min_frozen_days": min_frozen_days,
            "reference_time": reference_time.isoformat(sep=" "),
            "cutoff_time": cutoff.isoformat(sep=" "),
        }
    )
    return {
        "meta": meta,
        "services": services,
    }


async def get_service_health(svcname: str) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    try:
        service_response = await get_service(svcname)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return _unknown_service_health(svcname)
        raise

    service_rows = service_response.get("data", [])
    if not service_rows:
        return _unknown_service_health(svcname)

    service = service_rows[0]
    instances_response = await get_service_instances(svcname)
    instances = instances_response.get("data", [])
    issues = _service_health_issues(service, instances)
    severity = _worst_issue_severity(issues)
    return {
        "overall": _service_health_overall(severity),
        "severity": severity,
        "service": _service_health_service_summary(service),
        "issues": issues,
        "signals": _service_health_signals(instances),
    }


async def list_service_props() -> dict[str, Any]:
    response = await collector_get("/services", params={"props": "svcname"})
    available_props = response.get("meta", {}).get("available_props", [])
    service_props = [
        prop.removeprefix("services.")
        for prop in available_props
        if isinstance(prop, str)
    ]

    return {
        "count": len(available_props),
        "available_props": available_props,
        "service_props": service_props,
    }


async def _resolve_tag_by_name(tag_name: str) -> dict[str, Any] | None:
    response = await collector_get(
        "/tags",
        params=[
            ("filters", f"tag_name={tag_name}"),
            ("props", TAG_LOOKUP_PROPS),
            ("limit", 1),
            ("offset", 0),
        ],
    )
    rows = response.get("data", [])
    if not rows:
        return None
    return rows[0]


def _ensure_props_include(props: str, required_prop: str) -> str:
    parts = [part.strip() for part in props.split(",") if part.strip()]
    if not parts:
        return required_prop
    normalized = {part.rsplit(":", 1)[-1].rsplit(".", 1)[-1] for part in parts}
    if required_prop not in normalized:
        parts.append(required_prop)
    return ",".join(parts)


def _dedupe_service_rows_by_name(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    services: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        svcname = str(row.get("svcname", "")).strip()
        if not svcname or svcname in seen:
            continue
        seen.add(svcname)
        services.append(row)
    return services


def _parse_service_config_sections(config_text: str) -> list[dict[str, Any]]:
    if not config_text.strip():
        return []

    parser = ConfigParser(interpolation=None, strict=False)
    parser.optionxform = str
    try:
        parser.read_string(config_text)
    except ConfigParserError:
        return []

    sections: list[dict[str, Any]] = []
    if parser.defaults():
        sections.append({"name": "DEFAULT", "options": dict(parser.defaults())})

    for section_name in parser.sections():
        section = parser[section_name]
        options = {
            key: value
            for key, value in section.items()
            if key not in parser.defaults()
        }
        sections.append({"name": section_name, "options": options})
    return sections


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


def _service_tag_filters(
    raw_filters: dict[str, str] | str | None = None,
    **criteria: str | None,
) -> list[tuple[str, str]]:
    filters = [
        (_service_tag_filter_field(field), value)
        for field, value in _parse_service_filters(raw_filters)
    ]
    for field, value in criteria.items():
        if value is None:
            continue
        value = value.strip()
        if value:
            filters.append((_service_tag_filter_field(field), value))
    return filters


def _service_tag_filter_field(field: str) -> str:
    if "." in field:
        return field
    return {
        "tag_name": "tags.tag_name",
        "tag_id": "tags.tag_id",
        "tag_data": "tags.tag_data",
        "tag_exclude": "tags.tag_exclude",
        "tag_created": "tags.tag_created",
    }.get(field, field)


def _service_tag_params(
    filters: list[tuple[str, str]],
    props: str,
) -> list[tuple[str, Any]]:
    params: list[tuple[str, Any]] = [("props", props)]
    for field, value in filters:
        params.append(("filters", f"{field}={value}"))
    return params


def _service_check_filters(
    raw_filters: dict[str, str] | str | None = None,
    **criteria: str | None,
) -> list[tuple[str, str]]:
    filters = [
        (_service_check_filter_field(field), value)
        for field, value in _parse_service_filters(raw_filters)
    ]
    for field, value in criteria.items():
        if value is None:
            continue
        value = value.strip()
        if value:
            filters.append((_service_check_filter_field(field), value))
    return filters


def _service_check_filter_field(field: str) -> str:
    if "." in field:
        return field
    return {
        "id": "checks_live.id",
        "svc_id": "checks_live.svc_id",
        "node_id": "checks_live.node_id",
        "chk_type": "checks_live.chk_type",
        "chk_instance": "checks_live.chk_instance",
        "chk_value": "checks_live.chk_value",
        "chk_err": "checks_live.chk_err",
        "chk_low": "checks_live.chk_low",
        "chk_high": "checks_live.chk_high",
        "chk_threshold_provider": "checks_live.chk_threshold_provider",
        "chk_created": "checks_live.chk_created",
        "chk_updated": "checks_live.chk_updated",
    }.get(field, field)


def _service_check_params(
    filters: list[tuple[str, str]],
    props: str,
) -> list[tuple[str, Any]]:
    params: list[tuple[str, Any]] = [("props", props)]
    for field, value in filters:
        params.append(("filters", f"{field}={value}"))
    return params


def _service_alert_filters(
    raw_filters: dict[str, str] | str | None = None,
    **criteria: str | None,
) -> list[tuple[str, str]]:
    filters = [
        (_service_alert_filter_field(field), value)
        for field, value in _parse_service_filters(raw_filters)
    ]
    for field, value in criteria.items():
        if value is None:
            continue
        value = value.strip()
        if value:
            filters.append((_service_alert_filter_field(field), value))
    return filters


def _service_alert_filter_field(field: str) -> str:
    if "." in field:
        return field
    return {
        "id": "dashboard.id",
        "dash_type": "dashboard.dash_type",
        "dash_severity": "dashboard.dash_severity",
        "dash_created": "dashboard.dash_created",
        "dash_updated": "dashboard.dash_updated",
        "dash_env": "dashboard.dash_env",
        "dash_instance": "dashboard.dash_instance",
        "node_id": "dashboard.node_id",
        "svc_id": "dashboard.svc_id",
    }.get(field, field)


def _service_alert_params(
    filters: list[tuple[str, str]],
    props: str,
    limit: int,
    offset: int,
) -> list[tuple[str, Any]]:
    params: list[tuple[str, Any]] = [
        ("props", props),
        ("limit", limit),
        ("offset", offset),
    ]
    for field, value in filters:
        params.append(("filters", f"{field}={value}"))
    return params


def _service_action_props(
    include_status_log: bool,
    include_status_log_preview: bool,
) -> str:
    props = SERVICE_ACTIONS_PROPS.split(",")
    if include_status_log or include_status_log_preview:
        props.append(SERVICE_ACTIONS_LOG_PROP)
    return ",".join(props)


def _service_action_filters(
    raw_filters: dict[str, str] | str | None = None,
    **criteria: str | None,
) -> list[tuple[str, str]]:
    filters: list[tuple[str, str]] = []
    filters.extend(_parse_service_filters(raw_filters))
    for field, value in criteria.items():
        if value is None:
            continue
        value = value.strip()
        if value:
            filters.append((field, value))
    return filters


def _service_unacknowledged_error_filters(
    raw_filters: dict[str, str] | str | None = None,
    **criteria: str | None,
) -> list[tuple[str, str]]:
    filters = _service_action_filters(raw_filters, **criteria)
    for field, _ in filters:
        normalized = field.rsplit(".", 1)[-1]
        if normalized in {"status", "ack"}:
            raise ValueError(
                "status and ack filters are implicit for "
                "actions_unacknowledged_errors"
            )
    return filters


def _service_action_params(
    filters: list[tuple[str, str]],
    props: str,
    limit: int,
    offset: int,
) -> list[tuple[str, Any]]:
    params: list[tuple[str, Any]] = [
        ("props", props),
        ("limit", limit),
        ("offset", offset),
    ]
    for field, value in filters:
        params.append(("filters", f"{field}={value}"))
    return params


def _service_action_rows(
    rows: list[dict[str, Any]],
    include_status_log: bool,
    include_status_log_preview: bool,
    status_log_max_chars: int,
    latest_first: bool,
) -> list[dict[str, Any]]:
    shaped: list[dict[str, Any]] = []
    source_rows = reversed(rows) if latest_first else rows
    for row in source_rows:
        action = dict(row)
        status_log = action.get(SERVICE_ACTIONS_LOG_PROP)
        if status_log is not None and include_status_log_preview:
            action["status_log_preview"] = _truncate_text(
                str(status_log),
                status_log_max_chars,
            )
        if not include_status_log:
            action.pop(SERVICE_ACTIONS_LOG_PROP, None)
        shaped.append(action)
    return shaped


def _truncate_text(value: str, max_chars: int) -> str:
    if max_chars <= 0:
        return ""
    if len(value) <= max_chars:
        return value
    return f"{value[:max_chars]}..."


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _group_frozen_services(
    rows: list[dict[str, Any]],
    min_frozen_days: int,
    cutoff: datetime,
    reference_time: datetime,
) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for row in rows:
        svcname = row.get("svcname")
        if not svcname:
            continue
        svcname = str(svcname)
        service = grouped.setdefault(
            svcname,
            {
                "svcname": svcname,
                "svc_env": row.get("svc_env"),
                "svc_app": row.get("svc_app"),
                "svc_status": row.get("svc_status"),
                "svc_availstatus": row.get("svc_availstatus"),
                "svc_frozen": row.get("svc_frozen"),
                "svc_topology": row.get("svc_topology"),
                "nodes": [],
                "instances": [],
            },
        )
        for field in (
            "svc_env",
            "svc_app",
            "svc_status",
            "svc_availstatus",
            "svc_frozen",
            "svc_topology",
        ):
            if service.get(field) is None and row.get(field) is not None:
                service[field] = row.get(field)

        nodename = row.get("nodename")
        if nodename and nodename not in service["nodes"]:
            service["nodes"].append(nodename)

        frozen_at = _first_datetime(
            row.get("mon_frozen_at"),
            row.get("mon_encap_frozen_at"),
        )
        service["instances"].append(
            _compact_dict(
                {
                    "nodename": row.get("nodename"),
                    "mon_vmname": row.get("mon_vmname"),
                    "mon_availstatus": row.get("mon_availstatus"),
                    "mon_frozen": row.get("mon_frozen"),
                    "mon_frozen_at": row.get("mon_frozen_at"),
                    "mon_encap_frozen_at": row.get("mon_encap_frozen_at"),
                }
            )
        )
        if frozen_at and (
            not service.get("_frozen_since_dt")
            or frozen_at < service["_frozen_since_dt"]
        ):
            service["_frozen_since_dt"] = frozen_at

    services: list[dict[str, Any]] = []
    for service in grouped.values():
        frozen_since = service.pop("_frozen_since_dt", None)
        if min_frozen_days and (not frozen_since or frozen_since > cutoff):
            continue
        service["nodes"] = sorted(str(node) for node in service["nodes"])
        service["frozen_instance_count"] = len(service["instances"])
        if frozen_since:
            service["frozen_since"] = frozen_since.isoformat(sep=" ")
            service["frozen_days"] = max(0, (reference_time - frozen_since).days)
        services.append(service)

    return sorted(
        services,
        key=lambda service: (
            service.get("frozen_since") or "",
            service.get("svcname") or "",
        ),
    )


def _first_datetime(*values: Any) -> datetime | None:
    dates = [_parse_collector_datetime(value) for value in values]
    dates = [date for date in dates if date is not None]
    return min(dates) if dates else None


def _parse_collector_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def _service_health_issues(
    service: dict[str, Any],
    instances: list[dict[str, Any]],
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    _add_status_issue(
        issues,
        field="svc_status",
        value=service.get("svc_status"),
        label="service status",
    )
    _add_status_issue(
        issues,
        field="svc_availstatus",
        value=service.get("svc_availstatus"),
        label="service availability status",
    )

    svc_frozen = _normalized_value(service.get("svc_frozen"))
    if svc_frozen and svc_frozen not in {"thawed", "false", "0", "no"}:
        issues.append(
            {
                "severity": "warning",
                "field": "svc_frozen",
                "message": f"Service frozen state is {service.get('svc_frozen')}.",
            }
        )

    placement = _normalized_value(service.get("svc_placement"))
    if placement and placement != "optimal":
        issues.append(
            {
                "severity": "warning",
                "field": "svc_placement",
                "message": f"Service placement is {service.get('svc_placement')}.",
            }
        )

    if not instances:
        issues.append(
            {
                "severity": "warning",
                "field": "instances",
                "message": "No service instance rows were returned by Collector.",
            }
        )
        return issues

    up_instances = sum(
        1
        for instance in instances
        if _normalized_value(instance.get("mon_availstatus")) == "up"
    )
    service_availstatus = _normalized_value(service.get("svc_availstatus"))
    for instance in instances:
        nodename = instance.get("nodename") or "unknown node"
        mon_availstatus = _normalized_value(instance.get("mon_availstatus"))
        if (
            mon_availstatus
            and mon_availstatus != "up"
            and not (service_availstatus == "up" and up_instances > 0)
        ):
            issues.append(
                {
                    "severity": _status_severity(mon_availstatus),
                    "field": "mon_availstatus",
                    "message": (
                        f"Instance on {nodename} has monitor availability "
                        f"{instance.get('mon_availstatus')}."
                    ),
                }
            )

        if _is_truthy(instance.get("mon_frozen")):
            issues.append(
                {
                    "severity": "warning",
                    "field": "mon_frozen",
                    "message": f"Instance on {nodename} is frozen.",
                }
            )
        if instance.get("mon_frozen_at"):
            issues.append(
                {
                    "severity": "warning",
                    "field": "mon_frozen_at",
                    "message": (
                        f"Instance on {nodename} has frozen timestamp "
                        f"{instance.get('mon_frozen_at')}."
                    ),
                }
            )
        if instance.get("mon_encap_frozen_at"):
            issues.append(
                {
                    "severity": "warning",
                    "field": "mon_encap_frozen_at",
                    "message": (
                        f"Instance on {nodename} has encap frozen timestamp "
                        f"{instance.get('mon_encap_frozen_at')}."
                    ),
                }
            )

    if up_instances == 0:
        issues.append(
            {
                "severity": "critical",
                "field": "instances",
                "message": "No service instance is reported up.",
            }
        )
    return issues


def _unknown_service_health(svcname: str) -> dict[str, Any]:
    return {
        "overall": "unknown",
        "severity": "unknown",
        "service": {"svcname": svcname},
        "issues": [
            {
                "severity": "unknown",
                "field": "svcname",
                "message": "Service was not found in Collector.",
            }
        ],
        "signals": {
            "instance_count": 0,
            "nodes": [],
            "active_nodes": [],
            "inactive_nodes": [],
            "availability_counts": {},
            "instances": [],
        },
    }


def _add_status_issue(
    issues: list[dict[str, str]],
    field: str,
    value: Any,
    label: str,
) -> None:
    status = _normalized_value(value)
    if not status or status in {"up", "ok", "thawed"}:
        return
    issues.append(
        {
            "severity": _status_severity(status),
            "field": field,
            "message": f"{label.capitalize()} is {value}.",
        }
    )


def _status_severity(status: str) -> str:
    if status in {"down", "error", "err", "failed", "failure", "critical"}:
        return "critical"
    if status in {"warn", "warning", "frozen", "n/a", "unknown"}:
        return "warning"
    return "warning"


def _worst_issue_severity(issues: list[dict[str, str]]) -> str:
    severities = {issue.get("severity") for issue in issues}
    if "critical" in severities:
        return "critical"
    if "warning" in severities:
        return "warning"
    if "unknown" in severities:
        return "unknown"
    return "ok"


def _service_health_overall(severity: str) -> str:
    return {
        "ok": "healthy",
        "warning": "degraded",
        "critical": "critical",
        "unknown": "unknown",
    }.get(severity, "unknown")


def _service_health_service_summary(service: dict[str, Any]) -> dict[str, Any]:
    return {
        "svcname": service.get("svcname"),
        "svc_status": service.get("svc_status"),
        "svc_availstatus": service.get("svc_availstatus"),
        "svc_frozen": service.get("svc_frozen"),
        "svc_topology": service.get("svc_topology"),
        "svc_nodes": service.get("svc_nodes"),
        "svc_drpnodes": service.get("svc_drpnodes"),
        "svc_placement": service.get("svc_placement"),
        "svc_ha": service.get("svc_ha"),
        "updated": service.get("updated"),
        "svc_status_updated": service.get("svc_status_updated"),
    }


def _service_health_signals(instances: list[dict[str, Any]]) -> dict[str, Any]:
    nodes = sorted(
        {
            str(instance.get("nodename"))
            for instance in instances
            if instance.get("nodename")
        }
    )
    active_nodes = sorted(
        {
            str(instance.get("nodename"))
            for instance in instances
            if instance.get("nodename")
            and _normalized_value(instance.get("mon_availstatus")) == "up"
        }
    )
    inactive_nodes = sorted(set(nodes) - set(active_nodes))
    availability_counts: dict[str, int] = {}
    for instance in instances:
        status = str(instance.get("mon_availstatus") or "unknown")
        availability_counts[status] = availability_counts.get(status, 0) + 1

    return {
        "instance_count": len(instances),
        "nodes": nodes,
        "active_nodes": active_nodes,
        "inactive_nodes": inactive_nodes,
        "availability_counts": availability_counts,
        "instances": [_compact_dict(instance) for instance in instances],
    }


def _normalized_value(value: Any) -> str:
    return str(value).strip().lower() if value is not None else ""


def _is_truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return _normalized_value(value) in {"true", "1", "yes", "y", "on", "frozen"}


def _compact_dict(data: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in data.items() if value is not None}


def _service_search_filters(
    raw_filters: dict[str, str] | str | None = None,
    **criteria: str | None,
) -> list[tuple[str, str]]:
    filters: list[tuple[str, str]] = []
    filters.extend(_parse_service_filters(raw_filters))
    for field, value in criteria.items():
        if value is None:
            continue
        value = value.strip()
        if value:
            filters.append((field, value))
    return filters


def _parse_service_filters(raw_filters: dict[str, str] | str | None) -> list[tuple[str, str]]:
    if not raw_filters:
        return []
    if isinstance(raw_filters, dict):
        return [
            (field.strip(), value.strip())
            for field, value in raw_filters.items()
            if field.strip() and value.strip()
        ]

    filters: list[tuple[str, str]] = []
    for item in raw_filters.split(","):
        item = item.strip()
        if not item:
            continue
        if "=" not in item:
            raise ValueError("filters must use the format 'prop=value,prop=value'")
        field, value = item.split("=", 1)
        field = field.strip()
        value = value.strip()
        if not field or not value:
            raise ValueError("filters must not contain empty props or values")
        filters.append((field, value))
    return filters


def _service_instance_filters(filters: list[tuple[str, str]]) -> list[tuple[str, str]]:
    qualified: list[tuple[str, str]] = []
    for field, value in filters:
        qualified.append((_service_instance_filter_field(field), value))
    return qualified


def _service_instance_filter_field(field: str) -> str:
    if "." in field:
        return field
    return f"services.{field}"


def _service_search_params(
    filters: list[tuple[str, str]],
    props: str,
    limit: int,
    offset: int,
) -> list[tuple[str, Any]]:
    params: list[tuple[str, Any]] = [
        ("props", props),
        ("limit", limit),
        ("offset", offset),
    ]
    for field, value in filters:
        params.append(("filters", f"{field}={value}"))
    return params

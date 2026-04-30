from configparser import ConfigParser, Error as ConfigParserError
from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get, collector_get_all

from ._common import _parse_service_filters, _truncate_text


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
SERVICE_CONFIG_PROPS = "svcname,svc_config,svc_config_updated,updated"


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

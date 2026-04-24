from datetime import datetime
from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get


DEFAULT_SEARCH_NODE_PROPS = (
    "nodename,status,asset_env,node_env,loc_city,loc_country,"
    "app,team_responsible,os_name"
)
DEFAULT_INVENTORY_STATS_FIELDS = (
    "status",
    "asset_env",
    "node_env",
    "loc_city",
    "loc_country",
    "app",
    "os_name",
)
NODE_SERVICES_INSTANCE_PROPS = (
    "services.svcname:svcname,services.svc_status:svc_status,"
    "services.svc_env:svc_env,services.svc_app:svc_app,"
    "services.svc_topology:svc_topology,svcmon.mon_vmname:mon_vmname,"
    "svcmon.mon_availstatus:mon_availstatus,nodes.nodename:nodename"
)
NODE_CLUSTER_PROPS = "nodename,nodes.cluster_id:cluster_id,clusters.cluster_name:cluster_name"
NODE_NETWORK_PROPS = (
    "mac,net_team_responsible,intf,addr,prio,net_gateway,net_comment,"
    "net_end,net_netmask,mask,net_network,addr_type,net_broadcast,"
    "net_pvid,net_begin,flag_deprecated,addr_updated,net_id,net_name"
)


async def list_nodes(props: str | None = None) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if props:
        params["props"] = props
    return await collector_get("/nodes", params=params or None)


async def list_node_props() -> dict[str, Any]:
    response = await collector_get("/nodes", params={"props": "nodename"})
    available_props = response.get("meta", {}).get("available_props", [])
    node_props = [
        prop.removeprefix("nodes.")
        for prop in available_props
        if isinstance(prop, str)
    ]

    return {
        "count": len(available_props),
        "available_props": available_props,
        "node_props": node_props,
    }


async def search_nodes(
    filters: dict[str, str] | str | None = None,
    nodename_contains: str | None = None,
    status: str | None = None,
    asset_env: str | None = None,
    node_env: str | None = None,
    loc_city: str | None = None,
    loc_country: str | None = None,
    team_responsible: str | None = None,
    app: str | None = None,
    os_name: str | None = None,
    props: str | None = None,
    limit: int = 20,
    offset: int = 0,
    max_scan: int = 5000,
) -> dict[str, Any]:
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    max_scan = max(limit + offset, min(max_scan, 50000))
    selected_props = _props_with_required(props or DEFAULT_SEARCH_NODE_PROPS, "nodename")
    parsed_filters = _node_search_filters(
        filters,
        status=status,
        asset_env=asset_env,
        node_env=node_env,
        loc_city=loc_city,
        loc_country=loc_country,
        team_responsible=team_responsible,
        app=app,
        os_name=os_name,
    )

    if not nodename_contains:
        params = _node_search_params(
            filters=parsed_filters,
            props=selected_props,
            limit=limit,
            offset=offset,
        )
        return await collector_get("/nodes", params=params)

    needle = nodename_contains.strip().lower()
    if not needle:
        raise ValueError("nodename_contains must not be empty")

    matches: list[dict[str, Any]] = []
    scanned = 0
    api_offset = 0
    page_size = min(max(limit + offset, 100), 1000)
    total_candidates: int | None = None

    while scanned < max_scan:
        response = await collector_get(
            "/nodes",
            params=_node_search_params(
                filters=parsed_filters,
                props=selected_props,
                limit=min(page_size, max_scan - scanned),
                offset=api_offset,
            ),
        )
        meta = response.get("meta", {})
        data = response.get("data", [])
        if total_candidates is None:
            total_candidates = meta.get("total")

        for node in data:
            nodename = str(node.get("nodename", "")).lower()
            if needle in nodename:
                matches.append(node)

        count = len(data)
        scanned += count
        api_offset += count
        if count == 0 or count < page_size or len(matches) >= offset + limit:
            break

    result_data = matches[offset : offset + limit]
    complete = total_candidates is None or api_offset >= total_candidates
    return {
        "meta": {
            "count": len(result_data),
            "total": len(matches) if complete else None,
            "limit": limit,
            "offset": offset,
            "scanned": scanned,
            "max_scan": max_scan,
            "complete": complete,
            "filters": {
                "nodename_contains": nodename_contains,
                **{field: value for field, value in parsed_filters},
            },
            "included_props": selected_props.split(","),
        },
        "data": result_data,
    }


async def count_nodes(
    filters: dict[str, str] | str | None = None,
    status: str | None = None,
    asset_env: str | None = None,
    node_env: str | None = None,
    loc_city: str | None = None,
    loc_country: str | None = None,
    team_responsible: str | None = None,
    app: str | None = None,
    os_name: str | None = None,
) -> dict[str, Any]:
    parsed_filters = _node_search_filters(
        filters,
        status=status,
        asset_env=asset_env,
        node_env=node_env,
        loc_city=loc_city,
        loc_country=loc_country,
        team_responsible=team_responsible,
        app=app,
        os_name=os_name,
    )
    response = await collector_get(
        "/nodes",
        params=_node_search_params(
            filters=parsed_filters,
            props="nodename",
            limit=1,
            offset=0,
        ),
    )
    meta = response.get("meta", {})
    return {
        "count": meta.get("total"),
        "filters": {field: value for field, value in parsed_filters},
    }


async def get_node(nodename: str) -> dict[str, Any]:
    nodename = nodename.strip()
    if not nodename:
        raise ValueError("nodename must not be empty")

    return await collector_get(f"/nodes/{quote(nodename, safe='')}")


async def get_node_tags(nodename: str) -> dict[str, Any]:
    nodename = nodename.strip()
    if not nodename:
        raise ValueError("nodename must not be empty")

    return await collector_get(f"/nodes/{quote(nodename, safe='')}/tags")


async def search_node_by_tag(tag_name: str) -> dict[str, Any]:
    tag_name = tag_name.strip()
    if not tag_name:
        raise ValueError("tag_name must not be empty")

    tag_response = await collector_get(
        "/tags",
        params=[
            ("filters", f"tag_name={tag_name}"),
            ("limit", 1),
            ("offset", 0),
        ],
    )
    tag_rows = tag_response.get("data", [])
    if not tag_rows:
        return {
            "tag_name": tag_name,
            "tag_id": None,
            "meta": {"count": 0, "source": "tags"},
            "data": [],
        }

    tag = tag_rows[0]
    tag_id = tag.get("tag_id")
    if not tag_id:
        return {
            "tag_name": tag_name,
            "tag_id": None,
            "meta": {"count": 0, "source": "tags"},
            "data": [],
        }

    response = await collector_get(f"/tags/{quote(str(tag_id), safe='')}/nodes")
    return {
        "tag_name": tag_name,
        "tag_id": str(tag_id),
        "meta": response.get("meta", {}),
        "data": response.get("data", []),
    }


async def search_nodes_without_tag(tag_name: str) -> dict[str, Any]:
    tag_name = tag_name.strip()
    if not tag_name:
        raise ValueError("tag_name must not be empty")

    tagged = await search_node_by_tag(tag_name)
    tagged_names = {
        str(row.get("nodename")).strip()
        for row in tagged.get("data", [])
        if str(row.get("nodename", "")).strip()
    }

    all_nodes = await collector_get(
        "/nodes",
        params={"props": "nodename", "limit": 0, "offset": 0},
    )
    all_rows = all_nodes.get("data", [])
    data = [
        row
        for row in all_rows
        if str(row.get("nodename", "")).strip() not in tagged_names
    ]
    meta = all_nodes.get("meta", {})
    return {
        "tag_name": tag_name,
        "tag_id": tagged.get("tag_id"),
        "meta": {
            "count": len(data),
            "tagged_count": len(tagged_names),
            "total_nodes": meta.get("total", len(all_rows)),
            "source": "nodes - tags/<tag_id>/nodes",
        },
        "data": data,
    }


async def get_node_location(nodename: str) -> dict[str, Any]:
    response = await get_node(nodename)
    node = _first_node_row(response, nodename)
    raw = {
        "loc_country": node.get("loc_country"),
        "loc_city": node.get("loc_city"),
        "loc_building": node.get("loc_building"),
        "loc_room": node.get("loc_room"),
        "loc_floor": node.get("loc_floor"),
        "loc_rack": node.get("loc_rack"),
        "enclosure": node.get("enclosure"),
        "enclosureslot": node.get("enclosureslot"),
        "loc_addr": node.get("loc_addr"),
        "loc_zip": node.get("loc_zip"),
    }
    return {
        "nodename": nodename.strip(),
        "location": {
            "country": node.get("loc_country"),
            "city": node.get("loc_city"),
            "building": node.get("loc_building"),
            "room": node.get("loc_room"),
            "floor": node.get("loc_floor"),
            "rack": node.get("loc_rack"),
            "enclosure": node.get("enclosure"),
            "enclosure_slot": node.get("enclosureslot"),
            "address": node.get("loc_addr"),
            "zip": node.get("loc_zip"),
        },
        "raw": raw,
    }


async def get_node_organization(nodename: str) -> dict[str, Any]:
    response = await get_node(nodename)
    node = _first_node_row(response, nodename)
    raw = {
        "team_responsible": node.get("team_responsible"),
        "team_integ": node.get("team_integ"),
        "team_support": node.get("team_support"),
        "app": node.get("app"),
    }
    return {
        "nodename": nodename.strip(),
        "organization": {
            "responsible": node.get("team_responsible"),
            "integration": node.get("team_integ"),
            "support": node.get("team_support"),
            "app": node.get("app"),
        },
        "raw": raw,
    }


async def get_node_hardware(nodename: str) -> dict[str, Any]:
    response = await get_node(nodename)
    node = _first_node_row(response, nodename)
    raw = {
        "type": node.get("type"),
        "manufacturer": node.get("manufacturer"),
        "model": node.get("model"),
        "serial": node.get("serial"),
        "bios_version": node.get("bios_version"),
        "cpu_model": node.get("cpu_model"),
        "cpu_vendor": node.get("cpu_vendor"),
        "cpu_cores": node.get("cpu_cores"),
        "cpu_threads": node.get("cpu_threads"),
        "cpu_dies": node.get("cpu_dies"),
        "cpu_freq": node.get("cpu_freq"),
        "mem_bytes": node.get("mem_bytes"),
        "mem_banks": node.get("mem_banks"),
        "mem_slots": node.get("mem_slots"),
        "power_supply_nb": node.get("power_supply_nb"),
        "power_cabinet1": node.get("power_cabinet1"),
        "power_cabinet2": node.get("power_cabinet2"),
        "power_breaker1": node.get("power_breaker1"),
        "power_breaker2": node.get("power_breaker2"),
        "power_protect": node.get("power_protect"),
        "power_protect_breaker": node.get("power_protect_breaker"),
        "enclosure": node.get("enclosure"),
        "enclosureslot": node.get("enclosureslot"),
    }
    return {
        "nodename": nodename.strip(),
        "hardware": {
            "type": node.get("type"),
            "manufacturer": node.get("manufacturer"),
            "model": node.get("model"),
            "serial": node.get("serial"),
            "bios_version": node.get("bios_version"),
        },
        "cpu": {
            "model": node.get("cpu_model"),
            "vendor": node.get("cpu_vendor"),
            "cores": node.get("cpu_cores"),
            "threads": node.get("cpu_threads"),
            "dies": node.get("cpu_dies"),
            "frequency": node.get("cpu_freq"),
        },
        "memory": {
            "bytes": node.get("mem_bytes"),
            "banks": node.get("mem_banks"),
            "slots": node.get("mem_slots"),
        },
        "power": {
            "supply_count": node.get("power_supply_nb"),
            "cabinet1": node.get("power_cabinet1"),
            "cabinet2": node.get("power_cabinet2"),
            "breaker1": node.get("power_breaker1"),
            "breaker2": node.get("power_breaker2"),
            "protect": node.get("power_protect"),
            "protect_breaker": node.get("power_protect_breaker"),
        },
        "placement": {
            "enclosure": node.get("enclosure"),
            "enclosure_slot": node.get("enclosureslot"),
        },
        "raw": raw,
    }


async def get_node_hardware_components(nodename: str) -> dict[str, Any]:
    nodename = nodename.strip()
    if not nodename:
        raise ValueError("nodename must not be empty")

    response = await collector_get(f"/nodes/{quote(nodename, safe='')}/hardware")
    return {
        "nodename": nodename,
        "meta": response.get("meta", {}),
        "data": response.get("data", []),
    }


async def get_node_os(nodename: str) -> dict[str, Any]:
    response = await get_node(nodename)
    node = _first_node_row(response, nodename)
    raw = {
        "os_name": node.get("os_name"),
        "os_vendor": node.get("os_vendor"),
        "os_release": node.get("os_release"),
        "os_kernel": node.get("os_kernel"),
        "os_arch": node.get("os_arch"),
        "os_concat": node.get("os_concat"),
        "version": node.get("version"),
        "sp_version": node.get("sp_version"),
        "tz": node.get("tz"),
        "last_boot": node.get("last_boot"),
    }
    return {
        "nodename": nodename.strip(),
        "os": {
            "name": node.get("os_name"),
            "vendor": node.get("os_vendor"),
            "release": node.get("os_release"),
            "kernel": node.get("os_kernel"),
            "arch": node.get("os_arch"),
            "concat": node.get("os_concat"),
        },
        "runtime": {
            "version": node.get("version"),
            "service_pack": node.get("sp_version"),
            "timezone": node.get("tz"),
            "last_boot": node.get("last_boot"),
        },
        "raw": raw,
    }


async def get_node_cluster(nodename: str) -> dict[str, Any]:
    nodename = nodename.strip()
    if not nodename:
        raise ValueError("nodename must not be empty")

    response = await collector_get(
        "/nodes",
        params=[
            ("meta", "False"),
            ("props", NODE_CLUSTER_PROPS),
            ("filters", f"nodename={nodename}"),
            ("limit", 1),
            ("offset", 0),
        ],
    )
    data = response.get("data", [])
    row = data[0] if data else {"nodename": nodename}
    cluster_id = _empty_to_none(row.get("cluster_id"))
    cluster_name = _empty_to_none(row.get("cluster_name"))
    return {
        "nodename": nodename,
        "cluster": (
            {
                "id": cluster_id,
                "name": cluster_name,
            }
            if cluster_id or cluster_name
            else None
        ),
        "raw": {
            "nodename": row.get("nodename"),
            "cluster_id": row.get("cluster_id"),
            "cluster_name": row.get("cluster_name"),
        },
    }


async def get_node_network(nodename: str) -> dict[str, Any]:
    nodename = nodename.strip()
    if not nodename:
        raise ValueError("nodename must not be empty")

    response = await collector_get(
        f"/nodes/{quote(nodename, safe='')}/ips",
        params={"props": NODE_NETWORK_PROPS},
    )
    return {
        "nodename": nodename,
        "meta": response.get("meta", {}),
        "data": response.get("data", []),
    }


async def get_node_compliance(nodename: str) -> dict[str, Any]:
    nodename = nodename.strip()
    if not nodename:
        raise ValueError("nodename must not be empty")

    response = await collector_get(f"/nodes/{quote(nodename, safe='')}/compliance/status")
    return {
        "nodename": nodename,
        "meta": response.get("meta", {}),
        "data": response.get("data", []),
    }


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


async def get_node_health(nodename: str) -> dict[str, Any]:
    response = await get_node(nodename)
    data = response.get("data", [])
    if not data:
        return {
            "overall": "unknown",
            "severity": "unknown",
            "node": {"nodename": nodename},
            "issues": [
                {
                    "severity": "unknown",
                    "field": "nodename",
                    "message": "Node was not found in the Collector response.",
                }
            ],
            "signals": {},
        }

    node = data[0]
    issues = _node_health_issues(node)
    severity = _highest_issue_severity(issues)
    return {
        "overall": _node_health_overall(severity),
        "severity": severity,
        "node": {
            "nodename": node.get("nodename"),
            "status": node.get("status"),
            "asset_env": node.get("asset_env"),
            "node_env": node.get("node_env"),
            "app": node.get("app"),
            "loc_city": node.get("loc_city"),
        },
        "issues": issues,
        "signals": {
            "status": node.get("status"),
            "last_comm": node.get("last_comm"),
            "updated": node.get("updated"),
            "last_boot": node.get("last_boot"),
            "maintenance_end": node.get("maintenance_end"),
            "node_frozen": node.get("node_frozen"),
            "node_frozen_at": node.get("node_frozen_at"),
            "snooze_till": node.get("snooze_till"),
            "hw_obs_warn_date": node.get("hw_obs_warn_date"),
            "hw_obs_alert_date": node.get("hw_obs_alert_date"),
            "os_obs_warn_date": node.get("os_obs_warn_date"),
            "os_obs_alert_date": node.get("os_obs_alert_date"),
            "warranty_end": node.get("warranty_end"),
        },
    }


async def get_nodes_inventory_stats(
    fields: str | None = None,
    page_size: int = 1000,
    max_nodes: int = 200000,
) -> dict[str, Any]:
    selected_fields = _parse_stats_fields(fields)
    page_size = max(1, min(page_size, 5000))
    max_nodes = max(1, min(max_nodes, 500000))
    counters: dict[str, dict[str, int]] = {
        field: {}
        for field in selected_fields
    }
    scanned = 0
    offset = 0
    total: int | None = None

    while scanned < max_nodes:
        response = await collector_get(
            "/nodes",
            params={
                "props": ",".join(selected_fields),
                "limit": min(page_size, max_nodes - scanned),
                "offset": offset,
            },
        )
        meta = response.get("meta", {})
        data = response.get("data", [])
        if total is None:
            total = meta.get("total")

        for node in data:
            for field in selected_fields:
                value = _stats_value(node.get(field))
                counters[field][value] = counters[field].get(value, 0) + 1

        count = len(data)
        scanned += count
        offset += count
        if count == 0 or count < page_size:
            break

    complete = total is None or scanned >= total
    return {
        "meta": {
            "total": total,
            "scanned": scanned,
            "complete": complete,
            "page_size": page_size,
            "max_nodes": max_nodes,
            "fields": selected_fields,
        },
        "stats": {
            f"count_by_{field}": _sort_stats(counter)
            for field, counter in counters.items()
        },
    }


def _props_with_required(props: str, *required_props: str) -> str:
    selected = [prop.strip() for prop in props.split(",") if prop.strip()]
    for prop in required_props:
        if prop not in selected:
            selected.append(prop)
    return ",".join(selected)


def _node_search_filters(
    raw_filters: dict[str, str] | str | None = None,
    **criteria: str | None,
) -> list[tuple[str, str]]:
    filters: list[tuple[str, str]] = []
    filters.extend(_parse_node_filters(raw_filters))
    for field, value in criteria.items():
        if value is None:
            continue
        value = value.strip()
        if value:
            filters.append((field, value))
    return filters


def _parse_node_filters(raw_filters: dict[str, str] | str | None) -> list[tuple[str, str]]:
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


def _node_search_params(
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


def _split_service_nodes(raw_nodes: Any) -> list[str]:
    if raw_nodes is None:
        return []
    return [
        node.strip()
        for node in str(raw_nodes).replace("\n", ",").split(",")
        if node.strip()
    ]


def _first_node_row(response: dict[str, Any], nodename: str) -> dict[str, Any]:
    data = response.get("data", [])
    if data:
        return data[0]
    return {"nodename": nodename.strip()}


def _empty_to_none(value: Any) -> Any:
    if value == "":
        return None
    return value


def _node_health_issues(node: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    status = str(node.get("status") or "").lower()
    if status == "down":
        issues.append(
            {
                "severity": "critical",
                "field": "status",
                "message": "Node status is down.",
            }
        )
    elif status == "warn":
        issues.append(
            {
                "severity": "warning",
                "field": "status",
                "message": "Node status is warn.",
            }
        )
    elif not status:
        issues.append(
            {
                "severity": "unknown",
                "field": "status",
                "message": "Node status is missing.",
            }
        )

    for field in ("hw_obs_alert_date", "os_obs_alert_date"):
        if node.get(field):
            issues.append(
                {
                    "severity": "critical",
                    "field": field,
                    "message": f"Collector alert date is set for {field}.",
                }
            )

    for field in ("hw_obs_warn_date", "os_obs_warn_date"):
        if node.get(field):
            issues.append(
                {
                    "severity": "warning",
                    "field": field,
                    "message": f"Collector warning date is set for {field}.",
                }
            )

    if _truthy_node_value(node.get("node_frozen")):
        issues.append(
            {
                "severity": "warning",
                "field": "node_frozen",
                "message": "Node is frozen.",
            }
        )

    now = datetime.now()
    maintenance_end = _parse_collector_datetime(node.get("maintenance_end"))
    if maintenance_end and maintenance_end > now:
        issues.append(
            {
                "severity": "info",
                "field": "maintenance_end",
                "message": "Node is currently in a maintenance window.",
            }
        )

    snooze_till = _parse_collector_datetime(node.get("snooze_till"))
    if snooze_till and snooze_till > now:
        issues.append(
            {
                "severity": "info",
                "field": "snooze_till",
                "message": "Node alerts are currently snoozed.",
            }
        )

    if node.get("last_comm") is None:
        issues.append(
            {
                "severity": "unknown",
                "field": "last_comm",
                "message": "Last communication timestamp is missing.",
            }
        )

    return issues


def _highest_issue_severity(issues: list[dict[str, str]]) -> str:
    priority = {
        "critical": 4,
        "warning": 3,
        "unknown": 2,
        "info": 1,
    }
    if not issues:
        return "ok"
    return max(issues, key=lambda issue: priority.get(issue["severity"], 0))["severity"]


def _node_health_overall(severity: str) -> str:
    if severity == "critical":
        return "unhealthy"
    if severity == "warning":
        return "degraded"
    if severity == "unknown":
        return "unknown"
    return "healthy"


def _truthy_node_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "t", "yes", "y"}


def _parse_collector_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace(" ", "T"))
    except ValueError:
        return None


def _parse_stats_fields(fields: str | None) -> list[str]:
    if not fields:
        return list(DEFAULT_INVENTORY_STATS_FIELDS)
    selected = []
    for field in fields.split(","):
        field = field.strip()
        if field and field not in selected:
            selected.append(field)
    if not selected:
        raise ValueError("fields must contain at least one node property")
    return selected


def _stats_value(value: Any) -> str:
    if value is None or value == "":
        return "<empty>"
    return str(value)


def _sort_stats(counter: dict[str, int]) -> dict[str, int]:
    return dict(
        sorted(
            counter.items(),
            key=lambda item: (-item[1], item[0]),
        )
    )

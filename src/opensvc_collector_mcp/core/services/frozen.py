from datetime import datetime, timedelta
from typing import Any

from opensvc_collector_mcp.client import collector_get_all

from ._common import _parse_service_filters
from ._formatting import compact_dict
from .instances import _service_instance_filters


FROZEN_SERVICES_PROPS = (
    "services.svcname:svcname,services.svc_status:svc_status,"
    "services.svc_availstatus:svc_availstatus,services.svc_frozen:svc_frozen,"
    "services.svc_env:svc_env,services.svc_app:svc_app,"
    "services.svc_topology:svc_topology,nodes.nodename:nodename,"
    "svcmon.mon_vmname:mon_vmname,svcmon.mon_availstatus:mon_availstatus,"
    "svcmon.mon_frozen:mon_frozen,svcmon.mon_frozen_at:mon_frozen_at,"
    "svcmon.mon_encap_frozen_at:mon_encap_frozen_at"
)


async def search_frozen_services(
    filters: dict[str, str] | str | None = None,
    min_frozen_days: int = 0,
    page_size: int = 1000,
    max_instances: int = 200000,
) -> dict[str, Any]:
    min_frozen_days = max(0, min(min_frozen_days, 3650))
    parsed_filters = _parse_service_filters(filters)
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
            compact_dict(
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

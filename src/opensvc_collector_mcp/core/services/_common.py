from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get
from opensvc_collector_mcp.core.prechecks import (
    clean_value,
    require_at_least_one_selector,
    require_identity,
    require_match,
    require_single_row,
)
from opensvc_collector_mcp.core.collection import collection_params


DEFAULT_SERVICE_SELECTOR_PROPS = "svc_id,svcname,svc_status,svc_availstatus,updated"


async def get_service_identity(svcname: str) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    response = await collector_get(
        f"/services/{quote(svcname, safe='')}",
        params={"props": DEFAULT_SERVICE_SELECTOR_PROPS},
    )
    rows = response.get("data", [])
    service = rows[0] if rows else {"svcname": svcname}
    return {
        "svcname": service.get("svcname") or svcname,
        "svc_id": service.get("svc_id"),
        "service": service,
    }


async def resolve_service_reference(
    *,
    svc_id: str | None = None,
    svcname: str | None = None,
    props: str = DEFAULT_SERVICE_SELECTOR_PROPS,
    operation: str = "service operation",
    missing_message: str | None = None,
    correlation_message: str = "svcname must match the resolved svc_id",
) -> dict[str, Any]:
    selectors = require_at_least_one_selector(
        operation,
        {"svc_id": svc_id, "svcname": svcname},
        selector_kind="service",
        message=missing_message,
    )
    service = await _resolve_service_by_preferred_selector(
        svc_id=selectors["svc_id"],
        svcname=selectors["svcname"],
        props=props,
        operation=operation,
    )
    _, resolved_svcname = require_identity(
        service,
        operation=operation,
        target="service",
        id_field="svc_id",
        name_field="svcname",
    )
    require_match(
        selectors["svcname"],
        resolved_svcname,
        message=correlation_message,
    )
    return service


async def _resolve_service_by_preferred_selector(
    *,
    svc_id: str,
    svcname: str,
    props: str,
    operation: str,
) -> dict[str, Any]:
    if svc_id:
        return await _resolve_service_id_selector(
            svc_id=svc_id,
            props=props,
            operation=operation,
        )
    return await _resolve_svcname_selector(
        svcname=svcname,
        props=props,
        operation=operation,
    )


async def _resolve_service_id_selector(
    *,
    svc_id: str,
    props: str,
    operation: str,
) -> dict[str, Any]:
    response = await collector_get(
        f"/services/{quote(svc_id, safe='')}",
        params={"props": props},
    )
    service = require_single_row(
        response,
        not_found_message=f"{operation} svc_id not found: {svc_id}",
        multiple_message=f"{operation} svc_id resolved to multiple services: {svc_id}",
        invalid_message=f"{operation} resolved service payload is invalid",
    )

    resolved_svc_id = clean_value(service.get("svc_id"))
    if resolved_svc_id != svc_id:
        raise ValueError(
            f"{operation} svc_id selector did not resolve to the exact svc_id; "
            "retry with a svc_id from list_services"
        )
    return service


async def _resolve_svcname_selector(
    *,
    svcname: str,
    props: str,
    operation: str,
) -> dict[str, Any]:
    response = await collector_get(
        "/services",
        params=collection_params(
            filters=[("svcname", svcname)],
            props=props,
            orderby=None,
            search=None,
            limit=2,
            offset=0,
        ),
    )
    return require_single_row(
        response,
        not_found_message=f"{operation} svcname not found: {svcname}",
        multiple_message=(
            f"{operation} svcname is ambiguous: {svcname}; "
            "retry with svc_id from list_services"
        ),
        invalid_message=f"{operation} resolved service payload is invalid",
        exact_match_field="svcname",
        exact_match_value=svcname,
    )


def _ensure_props_include(props: str, required_prop: str) -> str:
    parts = [part.strip() for part in props.split(",") if part.strip()]
    if not parts:
        return required_prop
    normalized = {part.rsplit(":", 1)[-1].rsplit(".", 1)[-1] for part in parts}
    if required_prop not in normalized:
        parts.append(required_prop)
    return ",".join(parts)


def _unresolved_node_ids(
    rows: list[dict[str, Any]],
    nodenames_by_node_id: dict[str, str],
) -> list[str]:
    return sorted(
        {
            node_id
            for row in rows
            if (node_id := str(row.get("node_id") or "").strip())
            and node_id not in nodenames_by_node_id
        }
    )


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


def _parse_service_filters(
    raw_filters: dict[str, str] | str | None,
) -> list[tuple[str, str]]:
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

from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import (
    collector_delete,
    collector_get,
    collector_get_all,
    collector_get_page,
    collector_post,
)
from opensvc_collector_mcp.core.prechecks import clean_value, require_single_row
from opensvc_collector_mcp.core.services._common import resolve_service_reference
from opensvc_collector_mcp.core.collection import collection_params, parse_collector_filters

from ._common import resolve_tag_reference
from ._read import dedupe_rows_by_key, ensure_props_include, resolve_tag_selector


DEFAULT_TAG_SERVICE_PROPS = (
    "svcname,svc_app,svc_env,svc_status,svc_availstatus,svc_topology,"
    "svc_nodes,svc_drpnodes,svc_frozen,svc_ha,svc_created,updated"
)
DEFAULT_TAG_SERVICE_WRITE_PROPS = (
    "svc_id,svcname,svc_app,svc_env,svc_status,"
    "svc_availstatus,svc_topology,updated"
)


async def attach_tag_to_service(
    *,
    tag_id: str | None = None,
    tag_name: str | None = None,
    svc_id: str | None = None,
    svcname: str | None = None,
) -> dict[str, Any]:
    selector_tag_id = clean_value(tag_id)
    selector_tag_name = clean_value(tag_name)
    selector_svc_id = clean_value(svc_id)
    selector_svcname = clean_value(svcname)

    tag = await resolve_tag_reference(
        tag_id=selector_tag_id or None,
        tag_name=selector_tag_name or None,
        operation="attach tag to service",
        missing_message="attach tag to service requires tag_id or tag_name",
    )
    service = await resolve_service_reference(
        svc_id=selector_svc_id or None,
        svcname=selector_svcname or None,
        props=DEFAULT_TAG_SERVICE_WRITE_PROPS,
        operation="attach tag to service",
        missing_message="attach tag to service requires svc_id or svcname",
    )

    resolved_tag_id = clean_value(tag.get("tag_id"))
    resolved_tag_name = clean_value(tag.get("tag_name"))
    resolved_svc_id = clean_value(service.get("svc_id"))
    resolved_svcname = clean_value(service.get("svcname"))

    path = (
        f"/tags/{quote(resolved_tag_id, safe='')}/services/"
        f"{quote(resolved_svc_id, safe='')}"
    )
    response = await collector_post(path)
    return {
        "tag_id": resolved_tag_id,
        "tag_name": resolved_tag_name,
        "tag": tag,
        "svc_id": resolved_svc_id,
        "svcname": resolved_svcname,
        "service": service,
        "attached": True,
        "collector_response": response,
        "meta": {
            "source": "tags/<tag_id>/services/<svc_id>",
            "tag_selector": (
                "tag_id+tag_name"
                if selector_tag_id and selector_tag_name
                else "tag_id" if selector_tag_id else "tag_name"
            ),
            "service_selector": (
                "svc_id+svcname"
                if selector_svc_id and selector_svcname
                else "svc_id" if selector_svc_id else "svcname"
            ),
        },
    }


async def detach_tag_from_service(
    *,
    tag_id: str | None = None,
    tag_name: str | None = None,
    svc_id: str | None = None,
    svcname: str | None = None,
) -> dict[str, Any]:
    selector_tag_id = clean_value(tag_id)
    selector_tag_name = clean_value(tag_name)
    selector_svc_id = clean_value(svc_id)
    selector_svcname = clean_value(svcname)

    tag = await resolve_tag_reference(
        tag_id=selector_tag_id or None,
        tag_name=selector_tag_name or None,
        operation="detach tag from service",
        missing_message="detach tag from service requires tag_id or tag_name",
    )
    service = await resolve_service_reference(
        svc_id=selector_svc_id or None,
        svcname=selector_svcname or None,
        props=DEFAULT_TAG_SERVICE_WRITE_PROPS,
        operation="detach tag from service",
        missing_message="detach tag from service requires svc_id or svcname",
    )

    resolved_tag_id = clean_value(tag.get("tag_id"))
    resolved_tag_name = clean_value(tag.get("tag_name"))
    resolved_svc_id = clean_value(service.get("svc_id"))
    resolved_svcname = clean_value(service.get("svcname"))
    relation = await _ensure_tag_service_relation_exists(
        tag_id=resolved_tag_id,
        svc_id=resolved_svc_id,
    )

    path = (
        f"/tags/{quote(resolved_tag_id, safe='')}/services/"
        f"{quote(resolved_svc_id, safe='')}"
    )
    response = await collector_delete(path)
    return {
        "tag_id": resolved_tag_id,
        "tag_name": resolved_tag_name,
        "tag": tag,
        "svc_id": resolved_svc_id,
        "svcname": resolved_svcname,
        "service": service,
        "relation": relation,
        "detached": True,
        "collector_response": response,
        "meta": {
            "source": "tags/<tag_id>/services/<svc_id>",
            "tag_selector": (
                "tag_id+tag_name"
                if selector_tag_id and selector_tag_name
                else "tag_id" if selector_tag_id else "tag_name"
            ),
            "service_selector": (
                "svc_id+svcname"
                if selector_svc_id and selector_svcname
                else "svc_id" if selector_svc_id else "svcname"
            ),
            "precheck": "tag_service_relation_exists",
        },
    }


async def count_tag_services(
    tag_id: str | None = None,
    tag_name: str | None = None,
    max_services: int = 200000,
) -> dict[str, Any]:
    resolved = await resolve_tag_selector(tag_id=tag_id, tag_name=tag_name)
    response = await collector_get_all(
        f"/tags/{quote(resolved['tag_id'], safe='')}/services",
        params={"props": "svcname"},
        max_items=max_services,
    )
    raw_rows = response.get("data", [])
    rows = dedupe_rows_by_key(raw_rows, "svcname")
    meta = dict(response.get("meta", {}))
    return {
        "tag_id": resolved["tag_id"],
        "tag_name": resolved.get("tag_name"),
        "tag": resolved.get("tag"),
        "count": len(rows),
        "raw_count": len(raw_rows),
        "duplicate_count": len(raw_rows) - len(rows),
        "meta": {
            **meta,
            "source": "tags/<tag_id>/services",
            "selector": resolved["selector"],
            "resolution": resolved["resolution"],
            "complete": meta.get("complete"),
            "max_services": max_services,
        },
    }


async def get_tag_services(
    tag_id: str | None = None,
    tag_name: str | None = None,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "svcname",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    resolved = await resolve_tag_selector(tag_id=tag_id, tag_name=tag_name)
    selected_props = ensure_props_include(
        props or DEFAULT_TAG_SERVICE_PROPS,
        "svcname",
    )
    response = await collector_get_page(
        f"/tags/{quote(resolved['tag_id'], safe='')}/services",
        params=collection_params(
            filters=parse_collector_filters(filters),
            props=selected_props,
            orderby=orderby,
            search=search,
            limit=limit,
            offset=offset,
        ),
    )
    return {
        "tag_id": resolved["tag_id"],
        "tag_name": resolved.get("tag_name"),
        "tag": resolved.get("tag"),
        **response,
    }


async def _ensure_tag_service_relation_exists(
    *,
    tag_id: str,
    svc_id: str,
) -> dict[str, Any]:
    response = await collector_get(
        f"/tags/{quote(tag_id, safe='')}/services",
        params=collection_params(
            filters=[("svc_id", svc_id)],
            props="svc_id,svcname",
            orderby=None,
            search=None,
            limit=2,
            offset=0,
        ),
    )
    return require_single_row(
        response,
        not_found_message=(
            "detach tag from service relation not found: "
            f"tag_id={tag_id} svc_id={svc_id}"
        ),
        multiple_message=(
            "detach tag from service relation is ambiguous or missing svc_id: "
            f"tag_id={tag_id} svc_id={svc_id}"
        ),
        invalid_message="detach tag from service resolved relation payload is invalid",
        exact_match_field="svc_id",
        exact_match_value=svc_id,
    )

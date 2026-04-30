from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get, collector_get_all

from ._common import _ensure_props_include, _parse_service_filters
from .inventory import DEFAULT_LIST_SERVICE_PROPS


SERVICE_TAGS_PROPS = (
    "tags.tag_name,tags.tag_id,tags.tag_data,tags.tag_exclude,"
    "tags.tag_created"
)
TAG_LOOKUP_PROPS = "tag_name,tag_id,tag_data,tag_exclude,tag_created"


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

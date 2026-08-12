from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get, collector_get_page
from opensvc_collector_mcp.core.collection import (
    collection_params,
    parse_collector_filters,
)

NODE_RELATION_PROPS = "node_id,nodename,app,node_env,status,updated"
SERVICE_RELATION_PROPS = (
    "svc_id,svcname,svc_app,svc_env,svc_status,svc_availstatus,updated"
)


def parse_filters(
    raw_filters: dict[str, str] | str | None,
) -> list[tuple[str, str]]:
    return parse_collector_filters(raw_filters)


def quote_path_id(value: int | str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError("id must not be empty")
    return quote(text, safe="")


async def get_collection_page(
    path: str,
    filters: list[tuple[str, str]] | None = None,
    props: str | None = None,
    orderby: str | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    limit = max(1, min(limit, 1000))
    offset = max(0, offset)
    return await collector_get_page(
        path,
        params=collection_params(
            filters=filters or [],
            props=props,
            orderby=orderby,
            search=search,
            limit=limit,
            offset=offset,
        ),
    )


async def get_object(path: str, props: str | None = None) -> dict[str, Any]:
    params = {"props": props} if props else None
    return await collector_get(path, params=params)


def ensure_props_include(props: str, required_prop: str) -> str:
    parts = [part.strip() for part in props.split(",") if part.strip()]
    if not parts:
        return required_prop
    normalized = {part.rsplit(":", 1)[-1].rsplit(".", 1)[-1] for part in parts}
    if required_prop not in normalized:
        parts.append(required_prop)
    return ",".join(parts)


def truncate_text(value: str, max_chars: int) -> str:
    if max_chars <= 0:
        return ""
    if len(value) <= max_chars:
        return value
    return f"{value[:max_chars]}..."


def int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def collection_response(
    response: dict[str, Any],
    source: str,
    filters: list[tuple[str, str]],
    props: str | None,
) -> dict[str, Any]:
    del source, filters, props
    return {
        "pagination": response["pagination"],
        "data": response.get("data", []),
    }


def object_response(
    response: dict[str, Any],
    source: str,
    object_id: int | str,
    props: str | None,
) -> dict[str, Any]:
    rows = response.get("data", [])
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": source,
            "object_id": str(object_id),
            "included_props": props.split(",") if props else meta.get("included_props", []),
            "output_count": len(rows),
        }
    )
    return {"object_id": str(object_id), "meta": meta, "data": rows}


def relation_response(
    response: dict[str, Any],
    source: str,
    object_id: int | str,
    relation: str,
    filters: list[tuple[str, str]],
    props: str | None,
) -> dict[str, Any]:
    data = collection_response(response, source, filters, props)
    data["object_id"] = str(object_id)
    data["relation"] = relation
    return data

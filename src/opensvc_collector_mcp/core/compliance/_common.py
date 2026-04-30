from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get


def quote_path_id(value: int | str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError("id must not be empty")
    return quote(text, safe="")


def parse_filters(raw_filters: dict[str, str] | str | None) -> list[tuple[str, str]]:
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


def collection_params(
    filters: list[tuple[str, str]],
    props: str | None,
    orderby: str | None,
    search: str | None,
    limit: int,
    offset: int,
) -> list[tuple[str, Any]]:
    params: list[tuple[str, Any]] = [
        ("limit", limit),
        ("offset", offset),
    ]
    if props:
        params.append(("props", props))
    if orderby:
        params.append(("orderby", orderby))
    if search:
        params.append(("search", search))
    for field, value in filters:
        params.append(("filters", f"{field}={value}"))
    return params


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
    return await collector_get(
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

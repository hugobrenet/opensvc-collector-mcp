from typing import Any


def parse_collector_filters(
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


def collection_params(
    *,
    filters: list[tuple[str, str]] | None = None,
    props: str | None = None,
    orderby: str | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[tuple[str, Any]]:
    limit = max(1, min(limit, 1000))
    offset = max(0, offset)
    params: list[tuple[str, Any]] = [("limit", limit), ("offset", offset)]
    if props:
        params.append(("props", props))
    if orderby:
        params.append(("orderby", orderby))
    if search:
        params.append(("search", search))
    for field, value in filters or []:
        params.append(("filters", f"{field}={value}"))
    return params

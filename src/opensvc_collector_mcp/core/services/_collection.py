from typing import Any


def collection_params(
    filters: list[tuple[str, str]],
    props: str,
    orderby: str | None,
    limit: int,
    offset: int,
    search: str | None = None,
) -> list[tuple[str, Any]]:
    params: list[tuple[str, Any]] = [
        ("props", props),
        ("limit", limit),
        ("offset", offset),
    ]
    if orderby:
        params.append(("orderby", orderby))
    if search:
        params.append(("search", search))
    for field, value in filters:
        params.append(("filters", f"{field}={value}"))
    return params

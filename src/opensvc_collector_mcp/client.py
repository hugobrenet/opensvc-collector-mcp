from collections.abc import Sequence
from typing import Any

import httpx

from opensvc_collector_mcp.auth.context import (
    CollectorCredentials,
    get_collector_credentials,
    reset_collector_credentials,
    set_collector_credentials,
)
from opensvc_collector_mcp.config import (
    HTTP_REQUEST_TIMEOUT_SECONDS,
    OPENSVC_API_BASE_URL,
)

__all__ = [
    "CollectorCredentials",
    "collector_get",
    "collector_get_page",
    "collector_get_all",
    "collector_get_with_credentials",
    "collector_delete",
    "collector_delete_with_credentials",
    "collector_post",
    "collector_post_with_credentials",
    "collector_put",
    "collector_put_with_credentials",
    "get_collector_credentials",
    "reset_collector_credentials",
    "set_collector_credentials",
    "validate_collector_credentials",
]


async def collector_get(
    path: str,
    params: dict[str, Any] | Sequence[tuple[str, Any]] | None = None,
) -> dict[str, Any]:
    credentials = get_collector_credentials()
    if credentials is None:
        raise RuntimeError("Missing Collector Basic Auth credentials from MCP request")

    return await collector_get_with_credentials(
        path=path,
        credentials=credentials,
        params=params,
    )


async def collector_get_page(
    path: str,
    params: dict[str, Any] | Sequence[tuple[str, Any]] | None = None,
    *,
    limit: int | None = None,
    offset: int | None = None,
) -> dict[str, Any]:
    """Return one lightweight Collector collection page.

    Collector metadata is disabled because property discovery and counts have
    dedicated tools. The public pagination state is derived from the requested
    page and returned row count instead.
    """
    if limit is None:
        limit = int(_last_param_value(params, "limit", 20))
    if offset is None:
        offset = int(_last_param_value(params, "offset", 0))
    limit = max(1, min(limit, 1000))
    offset = max(0, offset)
    response = await collector_get(
        path,
        params=_with_page_params(
            params=params,
            limit=limit,
            offset=offset,
        ),
    )
    data = response.get("data", [])
    if not isinstance(data, list):
        raise ValueError("Collector collection response data must be a list")

    returned = len(data)
    complete = returned < limit
    return {
        "pagination": {
            "limit": limit,
            "offset": offset,
            "returned": returned,
            "next_offset": None if complete else offset + returned,
            "complete": complete,
            "truncated": False,
        },
        "data": data,
    }


async def collector_post(
    path: str,
    data: dict[str, Any] | None = None,
    params: dict[str, Any] | Sequence[tuple[str, Any]] | None = None,
) -> dict[str, Any]:
    credentials = get_collector_credentials()
    if credentials is None:
        raise RuntimeError("Missing Collector Basic Auth credentials from MCP request")

    return await collector_post_with_credentials(
        path=path,
        credentials=credentials,
        data=data,
        params=params,
    )


async def collector_put(
    path: str,
    data: dict[str, Any] | None = None,
    params: dict[str, Any] | Sequence[tuple[str, Any]] | None = None,
) -> dict[str, Any]:
    credentials = get_collector_credentials()
    if credentials is None:
        raise RuntimeError("Missing Collector Basic Auth credentials from MCP request")

    return await collector_put_with_credentials(
        path=path,
        credentials=credentials,
        data=data,
        params=params,
    )


async def collector_delete(
    path: str,
    data: dict[str, Any] | None = None,
    params: dict[str, Any] | Sequence[tuple[str, Any]] | None = None,
) -> dict[str, Any]:
    credentials = get_collector_credentials()
    if credentials is None:
        raise RuntimeError("Missing Collector Basic Auth credentials from MCP request")

    return await collector_delete_with_credentials(
        path=path,
        credentials=credentials,
        data=data,
        params=params,
    )


async def collector_get_with_credentials(
    path: str,
    credentials: CollectorCredentials,
    params: dict[str, Any] | Sequence[tuple[str, Any]] | None = None,
) -> dict[str, Any]:
    if not OPENSVC_API_BASE_URL:
        raise RuntimeError("Missing environment variable: OPENSVC_API_BASE_URL")

    url = f"{OPENSVC_API_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    async with httpx.AsyncClient(
        verify=False,
        timeout=HTTP_REQUEST_TIMEOUT_SECONDS,
    ) as client:
        response = await client.get(
            url,
            params=params,
            auth=(credentials.username, credentials.password),
            headers={"Accept": "application/json"},
        )
    response.raise_for_status()
    return response.json()


async def collector_post_with_credentials(
    path: str,
    credentials: CollectorCredentials,
    data: dict[str, Any] | None = None,
    params: dict[str, Any] | Sequence[tuple[str, Any]] | None = None,
) -> dict[str, Any]:
    if not OPENSVC_API_BASE_URL:
        raise RuntimeError("Missing environment variable: OPENSVC_API_BASE_URL")

    url = f"{OPENSVC_API_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    async with httpx.AsyncClient(
        verify=False,
        timeout=HTTP_REQUEST_TIMEOUT_SECONDS,
    ) as client:
        response = await client.post(
            url,
            params=params,
            data=data,
            auth=(credentials.username, credentials.password),
            headers={"Accept": "application/json"},
        )
    response.raise_for_status()
    return response.json()


async def collector_put_with_credentials(
    path: str,
    credentials: CollectorCredentials,
    data: dict[str, Any] | None = None,
    params: dict[str, Any] | Sequence[tuple[str, Any]] | None = None,
) -> dict[str, Any]:
    if not OPENSVC_API_BASE_URL:
        raise RuntimeError("Missing environment variable: OPENSVC_API_BASE_URL")

    url = f"{OPENSVC_API_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    async with httpx.AsyncClient(
        verify=False,
        timeout=HTTP_REQUEST_TIMEOUT_SECONDS,
    ) as client:
        response = await client.put(
            url,
            params=params,
            data=data,
            auth=(credentials.username, credentials.password),
            headers={"Accept": "application/json"},
        )
    response.raise_for_status()
    return response.json()


async def collector_delete_with_credentials(
    path: str,
    credentials: CollectorCredentials,
    data: dict[str, Any] | None = None,
    params: dict[str, Any] | Sequence[tuple[str, Any]] | None = None,
) -> dict[str, Any]:
    if not OPENSVC_API_BASE_URL:
        raise RuntimeError("Missing environment variable: OPENSVC_API_BASE_URL")

    url = f"{OPENSVC_API_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    async with httpx.AsyncClient(
        verify=False,
        timeout=HTTP_REQUEST_TIMEOUT_SECONDS,
    ) as client:
        response = await client.request(
            "DELETE",
            url,
            params=params,
            data=data,
            auth=(credentials.username, credentials.password),
            headers={"Accept": "application/json"},
        )
    response.raise_for_status()
    return response.json()


async def validate_collector_credentials(
    credentials: CollectorCredentials,
) -> bool:
    try:
        await collector_get_with_credentials("/users/self", credentials=credentials)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code in {401, 403}:
            return False
        raise
    return True


async def collector_get_all(
    path: str,
    params: dict[str, Any] | Sequence[tuple[str, Any]] | None = None,
    page_size: int = 1000,
    max_items: int = 200000,
) -> dict[str, Any]:
    page_size = max(1, min(page_size, 5000))
    max_items = max(1, min(max_items, 500000))
    rows: list[dict[str, Any]] = []
    offset = 0
    complete = False

    while len(rows) < max_items:
        request_limit = min(page_size, max_items - len(rows))
        response = await collector_get_page(
            path,
            params=params,
            limit=request_limit,
            offset=offset,
        )
        data = response.get("data", [])
        rows.extend(data)

        count = len(data)
        offset += count
        if response["pagination"]["complete"]:
            complete = True
            break

    return {
        "meta": {
            "count": len(rows),
            "total": len(rows) if complete else None,
            "offset": 0,
            "complete": complete,
            "truncated": not complete,
            "max_items": max_items,
            "scanned": offset,
        },
        "data": rows,
    }


def _with_page_params(
    params: dict[str, Any] | Sequence[tuple[str, Any]] | None,
    *,
    limit: int,
    offset: int,
) -> dict[str, Any] | list[tuple[str, Any]]:
    if params is None:
        return {"limit": limit, "offset": offset, "meta": False}
    if isinstance(params, dict):
        merged = dict(params)
        merged.update({"limit": limit, "offset": offset, "meta": False})
        return merged

    filtered = [
        (key, value)
        for key, value in params
        if key not in {"limit", "offset", "meta"}
    ]
    filtered.extend(
        [
            ("limit", limit),
            ("offset", offset),
            ("meta", False),
        ]
    )
    return filtered


def _last_param_value(
    params: dict[str, Any] | Sequence[tuple[str, Any]] | None,
    key: str,
    default: Any,
) -> Any:
    if params is None:
        return default
    if isinstance(params, dict):
        return params.get(key, default)
    values = [value for item_key, value in params if item_key == key]
    return values[-1] if values else default

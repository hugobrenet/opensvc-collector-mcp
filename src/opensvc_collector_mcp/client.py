from collections.abc import Sequence
from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import Any

import httpx

from opensvc_collector_mcp.config import (
    HTTP_REQUEST_TIMEOUT_SECONDS,
    OPENSVC_API_BASE_URL,
)


@dataclass(frozen=True)
class CollectorCredentials:
    username: str
    password: str


_COLLECTOR_CREDENTIALS: ContextVar[CollectorCredentials | None] = ContextVar(
    "collector_credentials",
    default=None,
)


def set_collector_credentials(
    credentials: CollectorCredentials,
) -> Token[CollectorCredentials | None]:
    return _COLLECTOR_CREDENTIALS.set(credentials)


def reset_collector_credentials(token: Token[CollectorCredentials | None]) -> None:
    _COLLECTOR_CREDENTIALS.reset(token)


def get_collector_credentials() -> CollectorCredentials | None:
    return _COLLECTOR_CREDENTIALS.get()


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
    total: int | None = None
    first_meta: dict[str, Any] = {}

    while len(rows) < max_items:
        response = await collector_get(
            path,
            params=_with_limit_offset(
                params=params,
                limit=min(page_size, max_items - len(rows)),
                offset=offset,
            ),
        )
        meta = response.get("meta", {})
        data = response.get("data", [])
        if not first_meta:
            first_meta = dict(meta)
        if total is None:
            total = meta.get("total")

        rows.extend(data)

        count = len(data)
        offset += count
        if count == 0 or count < page_size:
            break
        if total is not None and offset >= total:
            break

    complete = total is None or offset >= total
    merged_meta = dict(first_meta)
    merged_meta.update(
        {
            "count": len(rows),
            "total": total if complete else None,
            "offset": 0,
            "complete": complete,
            "max_items": max_items,
            "scanned": offset,
        }
    )
    return {
        "meta": merged_meta,
        "data": rows,
    }


def _with_limit_offset(
    params: dict[str, Any] | Sequence[tuple[str, Any]] | None,
    limit: int,
    offset: int,
) -> dict[str, Any] | list[tuple[str, Any]]:
    if params is None:
        return {"limit": limit, "offset": offset}
    if isinstance(params, dict):
        merged = dict(params)
        merged["limit"] = limit
        merged["offset"] = offset
        return merged

    filtered = [(key, value) for key, value in params if key not in {"limit", "offset"}]
    filtered.append(("limit", limit))
    filtered.append(("offset", offset))
    return filtered

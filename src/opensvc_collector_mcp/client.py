from collections.abc import Sequence
from typing import Any

import httpx

from opensvc_collector_mcp.config import (
    OPENSVC_API_BASE_URL,
    OPENSVC_PASSWORD,
    OPENSVC_USER,
)


async def collector_get(
    path: str,
    params: dict[str, Any] | Sequence[tuple[str, Any]] | None = None,
) -> dict[str, Any]:
    if not OPENSVC_API_BASE_URL:
        raise RuntimeError("Missing environment variable: OPENSVC_API_BASE_URL")
    if not OPENSVC_USER:
        raise RuntimeError("Missing environment variable: OPENSVC_USER")
    if not OPENSVC_PASSWORD:
        raise RuntimeError("Missing environment variable: OPENSVC_PASSWORD")

    url = f"{OPENSVC_API_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    async with httpx.AsyncClient(verify=False, timeout=30) as client:
        response = await client.get(
            url,
            params=params,
            auth=(OPENSVC_USER, OPENSVC_PASSWORD),
            headers={"Accept": "application/json"},
        )
    response.raise_for_status()
    return response.json()


async def collector_get_all(
    path: str,
    params: dict[str, Any] | Sequence[tuple[str, Any]] | None = None,
    strategy: str = "paged",
    page_size: int = 1000,
    max_items: int = 200000,
) -> dict[str, Any]:
    if strategy == "limit_zero":
        response = await collector_get(
            path,
            params=_with_limit_offset(params=params, limit=0, offset=0),
        )
        meta = dict(response.get("meta", {}))
        data = response.get("data", [])
        meta.update(
            {
                "count": len(data),
                "offset": 0,
                "complete": True,
                "strategy": strategy,
            }
        )
        return {
            "meta": meta,
            "data": data,
        }

    if strategy != "paged":
        raise ValueError(f"Unsupported collector_get_all strategy: {strategy}")

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
            "page_size": page_size,
            "max_items": max_items,
            "scanned": offset,
            "strategy": strategy,
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

    filtered = [
        (key, value)
        for key, value in params
        if key not in {"limit", "offset"}
    ]
    filtered.append(("limit", limit))
    filtered.append(("offset", offset))
    return filtered

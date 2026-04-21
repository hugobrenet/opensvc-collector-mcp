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

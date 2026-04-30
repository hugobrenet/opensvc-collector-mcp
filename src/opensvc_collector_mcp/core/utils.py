import asyncio
from collections.abc import Iterable
from typing import Any

from opensvc_collector_mcp.client import collector_get


async def get_nodename_by_node_id(node_id: str) -> str | None:
    node_id = node_id.strip()
    if not node_id:
        return None

    response = await collector_get(
        "/nodes",
        params=[
            ("filters", f"node_id={node_id}"),
            ("props", "node_id,nodename"),
            ("limit", 1),
            ("offset", 0),
        ],
    )
    rows = response.get("data", [])
    if not rows:
        return None
    nodename = rows[0].get("nodename")
    return str(nodename).strip() if nodename else None


async def get_nodenames_by_node_ids(node_ids: Iterable[str]) -> dict[str, str]:
    unique_node_ids = sorted(
        {str(node_id).strip() for node_id in node_ids if str(node_id).strip()}
    )
    if not unique_node_ids:
        return {}

    results = await asyncio.gather(
        *(get_nodename_by_node_id(node_id) for node_id in unique_node_ids),
    )
    return {
        node_id: nodename
        for node_id, nodename in zip(unique_node_ids, results, strict=True)
        if nodename
    }


def enrich_rows_with_nodenames(
    rows: list[dict[str, Any]],
    nodenames_by_node_id: dict[str, str],
) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        node_id = str(item.get("node_id") or "").strip()
        nodename = nodenames_by_node_id.get(node_id)
        if nodename:
            item["nodename"] = nodename
        enriched.append(item)
    return enriched


async def get_svcname_by_svc_id(svc_id: str) -> str | None:
    svc_id = svc_id.strip()
    if not svc_id:
        return None

    response = await collector_get(
        "/services",
        params=[
            ("filters", f"svc_id={svc_id}"),
            ("props", "svc_id,svcname"),
            ("limit", 1),
            ("offset", 0),
        ],
    )
    rows = response.get("data", [])
    if not rows:
        return None
    svcname = rows[0].get("svcname")
    return str(svcname).strip() if svcname else None


async def get_svcnames_by_svc_ids(svc_ids: Iterable[str]) -> dict[str, str]:
    unique_svc_ids = sorted(
        {str(svc_id).strip() for svc_id in svc_ids if str(svc_id).strip()}
    )
    if not unique_svc_ids:
        return {}

    results = await asyncio.gather(
        *(get_svcname_by_svc_id(svc_id) for svc_id in unique_svc_ids),
    )
    return {
        svc_id: svcname
        for svc_id, svcname in zip(unique_svc_ids, results, strict=True)
        if svcname
    }


def enrich_rows_with_svcnames(
    rows: list[dict[str, Any]],
    svcnames_by_svc_id: dict[str, str],
) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        svc_id = str(item.get("svc_id") or "").strip()
        svcname = svcnames_by_svc_id.get(svc_id)
        if svcname:
            item["svcname"] = svcname
        enriched.append(item)
    return enriched

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


def parse_collector_filters(raw_filters: dict[str, str] | str | None) -> list[tuple[str, str]]:
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


def collection_meta(
    response: dict[str, Any],
    *,
    source: str,
    filters: list[tuple[str, str]] | None = None,
    props: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rows = response.get("data", [])
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": source,
            "filter": {field: value for field, value in filters or []},
            "included_props": props.split(",") if props else meta.get("included_props", []),
            "output_count": len(rows),
        }
    )
    if extra:
        meta.update(extra)
    return meta

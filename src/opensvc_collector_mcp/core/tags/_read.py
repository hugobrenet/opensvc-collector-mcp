from typing import Any

from opensvc_collector_mcp.client import collector_get
from opensvc_collector_mcp.core.utils import collection_params


async def resolve_tag_selector(
    tag_id: str | None = None,
    tag_name: str | None = None,
) -> dict[str, Any]:
    cleaned_tag_id = tag_id.strip() if tag_id else None
    cleaned_tag_name = tag_name.strip() if tag_name else None
    if bool(cleaned_tag_id) == bool(cleaned_tag_name):
        raise ValueError("provide exactly one of tag_id or tag_name")

    if cleaned_tag_id:
        return {
            "selector": cleaned_tag_id,
            "resolution": "tag_id",
            "tag_id": cleaned_tag_id,
        }

    response = await collector_get(
        "/tags",
        params=collection_params(
            filters=[("tag_name", cleaned_tag_name or "")],
            props="tag_id,tag_name",
            orderby=None,
            search=None,
            limit=2,
            offset=0,
        ),
    )
    rows = response.get("data", [])
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"tag_name {cleaned_tag_name!r} not found")

    exact_rows = [
        row for row in rows if str(row.get("tag_name") or "") == cleaned_tag_name
    ]
    if len(exact_rows) != 1:
        raise ValueError(
            f"tag_name {cleaned_tag_name!r} matched {len(exact_rows)} tags"
        )

    row = exact_rows[0]
    resolved_tag_id = str(row.get("tag_id") or "").strip()
    if not resolved_tag_id:
        raise ValueError(f"tag_name {cleaned_tag_name!r} resolved without tag_id")
    return {
        "selector": cleaned_tag_name,
        "resolution": "tag_name",
        "tag_id": resolved_tag_id,
        "tag_name": row.get("tag_name"),
        "tag": row,
    }


def ensure_props_include(props: str, required: str) -> str:
    selected = [prop.strip() for prop in props.split(",") if prop.strip()]
    if required not in selected:
        selected.insert(0, required)
    return ",".join(selected)


def dedupe_rows_by_key(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        value = str(row.get(key, "")).strip()
        if not value or value in seen:
            continue
        seen.add(value)
        deduped.append(row)
    return deduped

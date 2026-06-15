from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get
from opensvc_collector_mcp.core.utils import collection_params


DEFAULT_TAG_SELECTOR_PROPS = "tag_id,tag_name,tag_exclude,tag_created,tag_data"


async def resolve_single_tag_selector(
    *,
    tag_id: str | None = None,
    tag_name: str | None = None,
    props: str = DEFAULT_TAG_SELECTOR_PROPS,
    operation: str = "tag operation",
) -> dict[str, Any]:
    tag_id = tag_id.strip() if tag_id else ""
    tag_name = tag_name.strip() if tag_name else ""
    if bool(tag_id) == bool(tag_name):
        raise ValueError(
            f"{operation} requires exactly one tag selector: tag_id or tag_name"
        )

    if tag_id:
        tag = await _resolve_tag_id_selector(
            tag_id=tag_id,
            props=props,
            operation=operation,
        )
    else:
        tag = await _resolve_tag_name_selector(
            tag_name=tag_name,
            props=props,
            operation=operation,
        )

    resolved_tag_id = str(tag.get("tag_id") or "").strip()
    resolved_tag_name = str(tag.get("tag_name") or "").strip()
    if not resolved_tag_id:
        raise ValueError(f"{operation} resolved tag has no tag_id")
    if not resolved_tag_name:
        raise ValueError(f"{operation} resolved tag has no tag_name")
    return tag


async def _resolve_tag_id_selector(
    *,
    tag_id: str,
    props: str,
    operation: str,
) -> dict[str, Any]:
    response = await collector_get(
        f"/tags/{quote(tag_id, safe='')}",
        params={"props": props},
    )
    rows = response.get("data", [])
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"{operation} tag_id not found: {tag_id}")
    if len(rows) != 1:
        raise ValueError(f"{operation} tag_id resolved to multiple tags: {tag_id}")
    tag = rows[0]
    if not isinstance(tag, dict):
        raise ValueError(f"{operation} resolved tag payload is invalid")

    resolved_tag_id = str(tag.get("tag_id") or "").strip()
    if resolved_tag_id != tag_id:
        raise ValueError(
            f"{operation} tag_id selector did not resolve to the exact tag_id; "
            "retry with a tag_id from list_tags"
        )
    return tag


async def _resolve_tag_name_selector(
    *,
    tag_name: str,
    props: str,
    operation: str,
) -> dict[str, Any]:
    response = await collector_get(
        "/tags",
        params=collection_params(
            filters=[("tag_name", tag_name)],
            props=props,
            orderby=None,
            search=None,
            limit=2,
            offset=0,
        ),
    )
    rows = response.get("data", [])
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"{operation} tag_name not found: {tag_name}")

    exact_rows = [row for row in rows if str(row.get("tag_name") or "") == tag_name]
    if len(exact_rows) != 1:
        raise ValueError(
            f"{operation} tag_name is ambiguous: {tag_name}; "
            "retry with tag_id from list_tags"
        )
    tag = exact_rows[0]
    if not isinstance(tag, dict):
        raise ValueError(f"{operation} resolved tag payload is invalid")
    return tag

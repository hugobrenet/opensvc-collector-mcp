from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_delete, collector_post

from ._common import resolve_single_tag_selector


async def create_tag(
    tag_name: str,
    tag_data: str | None = None,
    tag_exclude: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"tag_name": tag_name.strip()}
    if not payload["tag_name"]:
        raise ValueError("tag_name must not be empty")
    if tag_data is not None:
        payload["tag_data"] = tag_data
    if tag_exclude is not None:
        payload["tag_exclude"] = tag_exclude

    return await collector_post("/tags", data=payload)


async def delete_tag(
    *,
    tag_id: str | None = None,
    tag_name: str | None = None,
) -> dict[str, Any]:
    selector_tag_id = tag_id.strip() if tag_id else ""
    selector_tag_name = tag_name.strip() if tag_name else ""

    tag = await resolve_single_tag_selector(
        tag_id=selector_tag_id or None,
        tag_name=selector_tag_name or None,
        operation="delete tag",
    )
    resolved_tag_id = str(tag.get("tag_id") or "").strip()
    resolved_tag_name = str(tag.get("tag_name") or "").strip()

    response = await collector_delete(f"/tags/{quote(resolved_tag_id, safe='')}")
    return {
        "tag_id": resolved_tag_id,
        "tag_name": resolved_tag_name,
        "tag": tag,
        "deleted": True,
        "collector_response": response,
        "meta": {
            "source": "tags/<tag_id>",
            "selector": "tag_id" if selector_tag_id else "tag_name",
        },
    }

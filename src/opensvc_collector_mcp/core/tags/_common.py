from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get
from opensvc_collector_mcp.core.prechecks import (
    clean_value,
    require_at_least_one_selector,
    require_exactly_one_selector,
    require_identity,
    require_match,
    require_single_row,
)
from opensvc_collector_mcp.core.collection import collection_params


DEFAULT_TAG_SELECTOR_PROPS = "tag_id,tag_name,tag_exclude,tag_created,tag_data"


async def resolve_single_tag_selector(
    *,
    tag_id: str | None = None,
    tag_name: str | None = None,
    props: str = DEFAULT_TAG_SELECTOR_PROPS,
    operation: str = "tag operation",
) -> dict[str, Any]:
    selectors = require_exactly_one_selector(
        operation,
        {"tag_id": tag_id, "tag_name": tag_name},
        selector_kind="tag",
    )
    tag = await _resolve_tag_by_preferred_selector(
        tag_id=selectors["tag_id"],
        tag_name=selectors["tag_name"],
        props=props,
        operation=operation,
    )
    require_identity(
        tag,
        operation=operation,
        target="tag",
        id_field="tag_id",
        name_field="tag_name",
    )
    return tag


async def resolve_tag_reference(
    *,
    tag_id: str | None = None,
    tag_name: str | None = None,
    props: str = DEFAULT_TAG_SELECTOR_PROPS,
    operation: str = "tag operation",
    missing_message: str | None = None,
    correlation_message: str = "tag_name must match the resolved tag_id",
) -> dict[str, Any]:
    selectors = require_at_least_one_selector(
        operation,
        {"tag_id": tag_id, "tag_name": tag_name},
        selector_kind="tag",
        message=missing_message,
    )
    tag = await _resolve_tag_by_preferred_selector(
        tag_id=selectors["tag_id"],
        tag_name=selectors["tag_name"],
        props=props,
        operation=operation,
    )
    _, resolved_tag_name = require_identity(
        tag,
        operation=operation,
        target="tag",
        id_field="tag_id",
        name_field="tag_name",
    )
    require_match(
        selectors["tag_name"],
        resolved_tag_name,
        message=correlation_message,
    )
    return tag


async def _resolve_tag_by_preferred_selector(
    *,
    tag_id: str,
    tag_name: str,
    props: str,
    operation: str,
) -> dict[str, Any]:
    if tag_id:
        return await _resolve_tag_id_selector(
            tag_id=tag_id,
            props=props,
            operation=operation,
        )
    return await _resolve_tag_name_selector(
        tag_name=tag_name,
        props=props,
        operation=operation,
    )


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
    tag = require_single_row(
        response,
        not_found_message=f"{operation} tag_id not found: {tag_id}",
        multiple_message=f"{operation} tag_id resolved to multiple tags: {tag_id}",
        invalid_message=f"{operation} resolved tag payload is invalid",
    )

    resolved_tag_id = clean_value(tag.get("tag_id"))
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
    return require_single_row(
        response,
        not_found_message=f"{operation} tag_name not found: {tag_name}",
        multiple_message=(
            f"{operation} tag_name is ambiguous: {tag_name}; "
            "retry with tag_id from list_tags"
        ),
        invalid_message=f"{operation} resolved tag payload is invalid",
        exact_match_field="tag_name",
        exact_match_value=tag_name,
    )

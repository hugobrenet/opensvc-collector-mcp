from typing import Any

from ._common import (
    collection_response,
    get_collection_page,
    get_object,
    object_response,
    parse_filters,
    quote_path_id,
)
from ._ruleset import RULESET_PROPS


async def list_compliance_rulesets(
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "ruleset_name",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    selected_props = props or RULESET_PROPS
    parsed_filters = parse_filters(filters)
    response = await get_collection_page(
        "/compliance/rulesets",
        filters=parsed_filters,
        props=selected_props,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )
    return collection_response(
        response,
        "compliance_rulesets",
        parsed_filters,
        selected_props,
    )


async def get_compliance_ruleset(
    ruleset_id: int | str | None = None,
    ruleset_name: str | None = None,
    props: str | None = None,
) -> dict[str, Any]:
    selected_props = props or RULESET_PROPS
    resolved = await _resolve_ruleset_identity(
        ruleset_id=ruleset_id,
        ruleset_name=ruleset_name,
    )
    resolved_id = str(resolved["id"])
    path = f"/compliance/rulesets/{quote_path_id(resolved_id)}"
    response = await get_object(path, props=selected_props)
    data = object_response(
        response,
        "compliance_ruleset",
        resolved_id,
        selected_props,
    )
    rows = data.get("data", [])
    resolved_name = resolved.get("ruleset_name") or (
        rows[0].get("ruleset_name") if rows else None
    )
    data["ruleset_name"] = resolved_name
    data["meta"].update(
        {
            "requested_ruleset_id": str(ruleset_id).strip()
            if ruleset_id is not None
            else None,
            "requested_ruleset_name": ruleset_name,
            "resolved_ruleset_id": resolved_id,
            "resolved_ruleset_name": resolved_name,
        }
    )
    return data


async def get_compliance_ruleset_usage(
    ruleset_id: int | str | None = None,
    ruleset_name: str | None = None,
) -> dict[str, Any]:
    resolved = await _resolve_ruleset_identity(
        ruleset_id=ruleset_id,
        ruleset_name=ruleset_name,
    )
    resolved_id = str(resolved["id"])
    resolved_name = resolved.get("ruleset_name")
    path = f"/compliance/rulesets/{quote_path_id(resolved_id)}/usage"
    response = await get_object(path)
    usage = response.get("data", response)
    return {
        "object_id": resolved_id,
        "ruleset_name": resolved_name,
        "meta": {
            "source": "compliance_ruleset_usage",
            "object_id": resolved_id,
            "requested_ruleset_id": str(ruleset_id).strip()
            if ruleset_id is not None
            else None,
            "requested_ruleset_name": ruleset_name,
            "resolved_ruleset_id": resolved_id,
            "resolved_ruleset_name": resolved_name,
        },
        "data": usage,
    }


async def _resolve_ruleset_identity(
    ruleset_id: int | str | None,
    ruleset_name: str | None,
) -> dict[str, Any]:
    requested_id = str(ruleset_id).strip() if ruleset_id is not None else ""
    requested_name = ruleset_name.strip() if ruleset_name else ""
    if requested_id:
        return {"id": requested_id, "ruleset_name": requested_name or None}
    if not requested_name:
        raise ValueError("ruleset_id or ruleset_name must be provided")

    response = await get_collection_page(
        "/compliance/rulesets",
        filters=[("ruleset_name", requested_name)],
        props="id,ruleset_name",
        limit=2,
        offset=0,
    )
    rows = response.get("data", [])
    if not rows:
        raise ValueError(
            f"No compliance ruleset found for ruleset_name {requested_name!r}"
        )
    if len(rows) > 1:
        raise ValueError(
            f"Multiple compliance rulesets found for ruleset_name {requested_name!r}"
        )
    return rows[0]

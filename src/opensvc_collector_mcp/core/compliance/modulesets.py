from typing import Any

from ._common import (
    collection_response,
    get_collection_page,
    get_object,
    object_response,
    parse_filters,
    quote_path_id,
)


MODULESET_PROPS = "id,modset_name,modset_author,modset_updated"
MODULE_PROPS = (
    "id,modset_id,modset_mod_name,autofix,modset_mod_author,modset_mod_updated"
)


async def list_compliance_modulesets(
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "modset_name",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    selected_props = props or MODULESET_PROPS
    parsed_filters = parse_filters(filters)
    response = await get_collection_page(
        "/compliance/modulesets",
        filters=parsed_filters,
        props=selected_props,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )
    return collection_response(
        response,
        "compliance_modulesets",
        parsed_filters,
        selected_props,
    )


async def get_compliance_moduleset(
    moduleset_id: int | str | None = None,
    modset_name: str | None = None,
    props: str | None = None,
) -> dict[str, Any]:
    selected_props = props or MODULESET_PROPS
    resolved = await _resolve_moduleset_identity(
        moduleset_id=moduleset_id,
        modset_name=modset_name,
    )
    resolved_id = str(resolved["id"])
    path = f"/compliance/modulesets/{quote_path_id(resolved_id)}"
    response = await get_object(path, props=selected_props)
    data = object_response(
        response,
        "compliance_moduleset",
        resolved_id,
        selected_props,
    )
    rows = data.get("data", [])
    resolved_name = resolved.get("modset_name") or (
        rows[0].get("modset_name") if rows else None
    )
    data["modset_name"] = resolved_name
    data["meta"].update(
        {
            "requested_moduleset_id": str(moduleset_id).strip()
            if moduleset_id is not None
            else None,
            "requested_modset_name": modset_name,
            "resolved_moduleset_id": resolved_id,
            "resolved_modset_name": resolved_name,
        }
    )
    return data


async def get_compliance_moduleset_module(
    moduleset_id: int | str,
    module_id: int | str,
    props: str | None = None,
) -> dict[str, Any]:
    selected_props = props or MODULE_PROPS
    path = (
        f"/compliance/modulesets/{quote_path_id(moduleset_id)}"
        f"/modules/{quote_path_id(module_id)}"
    )
    response = await get_object(path, props=selected_props)
    data = object_response(
        response,
        "compliance_moduleset_module",
        module_id,
        selected_props,
    )
    data["moduleset_id"] = str(moduleset_id)
    return data


async def get_compliance_moduleset_usage(
    moduleset_id: int | str | None = None,
    modset_name: str | None = None,
) -> dict[str, Any]:
    resolved = await _resolve_moduleset_identity(
        moduleset_id=moduleset_id,
        modset_name=modset_name,
    )
    resolved_id = str(resolved["id"])
    resolved_name = resolved.get("modset_name")
    path = f"/compliance/modulesets/{quote_path_id(resolved_id)}/usage"
    response = await get_object(path)
    usage = response.get("data", response)
    return {
        "object_id": resolved_id,
        "modset_name": resolved_name,
        "meta": {
            "source": "compliance_moduleset_usage",
            "object_id": resolved_id,
            "requested_moduleset_id": str(moduleset_id).strip()
            if moduleset_id is not None
            else None,
            "requested_modset_name": modset_name,
            "resolved_moduleset_id": resolved_id,
            "resolved_modset_name": resolved_name,
        },
        "data": usage,
    }


async def _resolve_moduleset_identity(
    moduleset_id: int | str | None,
    modset_name: str | None,
) -> dict[str, Any]:
    requested_id = str(moduleset_id).strip() if moduleset_id is not None else ""
    requested_name = modset_name.strip() if modset_name else ""
    if requested_id:
        return {"id": requested_id, "modset_name": requested_name or None}
    if not requested_name:
        raise ValueError("moduleset_id or modset_name must be provided")

    response = await get_collection_page(
        "/compliance/modulesets",
        filters=[("modset_name", requested_name)],
        props="id,modset_name",
        limit=2,
        offset=0,
    )
    rows = response.get("data", [])
    if not rows:
        raise ValueError(
            f"No compliance moduleset found for modset_name {requested_name!r}"
        )
    if len(rows) > 1:
        raise ValueError(
            f"Multiple compliance modulesets found for modset_name {requested_name!r}"
        )
    return rows[0]

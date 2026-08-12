from typing import Any

from ._common import get_object, object_response, quote_path_id
from ._ruleset import ruleset_variable_props
from .ruleset_relations import get_compliance_ruleset_items
from .rulesets import _resolve_ruleset_identity


async def get_compliance_ruleset_variables(
    ruleset_id: int | str | None = None,
    ruleset_name: str | None = None,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "var_name",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
    include_var_value: bool = False,
) -> dict[str, Any]:
    resolved = await _resolve_ruleset_identity(
        ruleset_id=ruleset_id,
        ruleset_name=ruleset_name,
    )
    resolved_id = str(resolved["id"])
    resolved_name = resolved.get("ruleset_name")
    response = await get_compliance_ruleset_items(
        ruleset_id=resolved_id,
        relation="variables",
        filters=filters,
        props=props,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
        include_var_value=include_var_value,
    )
    response["ruleset_name"] = resolved_name
    return response


async def get_compliance_ruleset_variable(
    ruleset_id: int | str | None = None,
    ruleset_name: str | None = None,
    variable_id: int | str | None = None,
    props: str | None = None,
    include_var_value: bool = False,
) -> dict[str, Any]:
    if variable_id is None or not str(variable_id).strip():
        raise ValueError("variable_id must be provided")

    resolved = await _resolve_ruleset_identity(
        ruleset_id=ruleset_id,
        ruleset_name=ruleset_name,
    )
    resolved_id = str(resolved["id"])
    resolved_name = resolved.get("ruleset_name")
    resolved_variable_id = str(variable_id).strip()
    selected_props = props or ruleset_variable_props(include_var_value)
    path = (
        f"/compliance/rulesets/{quote_path_id(resolved_id)}"
        f"/variables/{quote_path_id(resolved_variable_id)}"
    )
    response = await get_object(path, props=selected_props)
    data = object_response(
        response,
        "compliance_ruleset_variable",
        resolved_variable_id,
        selected_props,
    )
    data["ruleset_id"] = resolved_id
    data["ruleset_name"] = resolved_name
    data["meta"].update(
        {
            "include_var_value": include_var_value,
            "requested_ruleset_id": str(ruleset_id).strip()
            if ruleset_id is not None
            else None,
            "requested_ruleset_name": ruleset_name,
            "resolved_ruleset_id": resolved_id,
            "resolved_ruleset_name": resolved_name,
            "variable_id": resolved_variable_id,
        }
    )
    return data

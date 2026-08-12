from copy import deepcopy
from typing import Any

from ._common import get_object, quote_path_id
from .modulesets import _resolve_moduleset_identity


async def get_compliance_moduleset_definition(
    moduleset_id: int | str | None = None,
    modset_name: str | None = None,
    include_variable_values: bool = False,
) -> dict[str, Any]:
    resolved = await _resolve_moduleset_identity(
        moduleset_id=moduleset_id,
        modset_name=modset_name,
    )
    resolved_id = str(resolved["id"])
    path = f"/compliance/modulesets/{quote_path_id(resolved_id)}/export"
    response = await get_object(path)
    definition = _shape_moduleset_definition(
        response,
        include_variable_values=include_variable_values,
    )
    resolved_name = resolved.get("modset_name") or _definition_moduleset_name(
        definition
    )
    meta = {
        "source": "compliance_moduleset_definition",
        "object_id": resolved_id,
        "requested_moduleset_id": str(moduleset_id).strip()
        if moduleset_id is not None
        else None,
        "requested_modset_name": modset_name,
        "resolved_moduleset_id": resolved_id,
        "resolved_modset_name": resolved_name,
        "include_variable_values": include_variable_values,
        "moduleset_count": len(definition.get("modulesets", [])),
        "ruleset_count": len(definition.get("rulesets", [])),
        "filterset_count": len(definition.get("filtersets", [])),
        "variable_count": _definition_variable_count(definition),
    }
    return {
        "object_id": resolved_id,
        "modset_name": resolved_name,
        "meta": meta,
        "definition": definition,
    }


def _shape_moduleset_definition(
    response: dict[str, Any],
    include_variable_values: bool,
) -> dict[str, Any]:
    definition = deepcopy(response)
    if include_variable_values:
        for variable in _definition_variables(definition):
            if "var_value" in variable:
                variable["var_value_included"] = True
        return definition

    for variable in _definition_variables(definition):
        if "var_value" in variable:
            variable.pop("var_value", None)
            variable["var_value_included"] = False
            variable["var_value_hidden"] = True
    return definition


def _definition_variables(definition: dict[str, Any]) -> list[dict[str, Any]]:
    variables: list[dict[str, Any]] = []
    for ruleset in definition.get("rulesets", []):
        if not isinstance(ruleset, dict):
            continue
        for variable in ruleset.get("variables", []):
            if isinstance(variable, dict):
                variables.append(variable)
    return variables


def _definition_variable_count(definition: dict[str, Any]) -> int:
    return len(_definition_variables(definition))


def _definition_moduleset_name(definition: dict[str, Any]) -> str | None:
    modulesets = definition.get("modulesets", [])
    if not modulesets or not isinstance(modulesets[0], dict):
        return None
    name = modulesets[0].get("modset_name")
    return str(name) if name else None

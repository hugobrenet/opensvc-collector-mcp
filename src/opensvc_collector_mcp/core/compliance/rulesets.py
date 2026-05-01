from typing import Any, Literal

from ._common import (
    NODE_RELATION_PROPS,
    SERVICE_RELATION_PROPS,
    collection_response,
    get_collection_page,
    get_object,
    object_response,
    parse_filters,
    quote_path_id,
    relation_response,
)

RULESET_PROPS = "id,ruleset_name,ruleset_type,ruleset_public"
RULESET_VARIABLE_PROPS = "id,ruleset_id,var_name,var_class,var_author,var_updated"
RULESET_VARIABLE_VALUE_PROP = "var_value"

RulesetRelation = Literal[
    "variables",
    "nodes",
    "services",
    "candidate_nodes",
    "candidate_services",
    "publications",
    "responsibles",
]


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
    return collection_response(response, "compliance_rulesets", parsed_filters, selected_props)


async def get_compliance_ruleset(
    ruleset_id: int | str,
    props: str | None = None,
) -> dict[str, Any]:
    selected_props = props or RULESET_PROPS
    path = f"/compliance/rulesets/{quote_path_id(ruleset_id)}"
    response = await get_object(path, props=selected_props)
    return object_response(response, "compliance_ruleset", ruleset_id, selected_props)


async def get_compliance_ruleset_items(
    ruleset_id: int | str,
    relation: RulesetRelation,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
    include_var_value: bool = False,
) -> dict[str, Any]:
    selected_props = props or _ruleset_relation_props(relation, include_var_value)
    parsed_filters = parse_filters(filters)
    path = f"/compliance/rulesets/{quote_path_id(ruleset_id)}/{relation}"
    response = await get_collection_page(
        path,
        filters=parsed_filters,
        props=selected_props,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )
    meta = dict(response.get("meta", {}))
    meta["include_var_value"] = include_var_value
    response = {**response, "meta": meta}
    return relation_response(
        response,
        "compliance_ruleset_items",
        ruleset_id,
        relation,
        parsed_filters,
        selected_props,
    )


async def get_compliance_ruleset_variable(
    ruleset_id: int | str,
    variable_id: int | str,
    props: str | None = None,
    include_var_value: bool = False,
) -> dict[str, Any]:
    selected_props = props or _ruleset_variable_props(include_var_value)
    path = (
        f"/compliance/rulesets/{quote_path_id(ruleset_id)}"
        f"/variables/{quote_path_id(variable_id)}"
    )
    response = await get_object(path, props=selected_props)
    data = object_response(response, "compliance_ruleset_variable", variable_id, selected_props)
    data["ruleset_id"] = str(ruleset_id)
    data["meta"]["include_var_value"] = include_var_value
    return data


async def get_compliance_ruleset_usage(ruleset_id: int | str) -> dict[str, Any]:
    path = f"/compliance/rulesets/{quote_path_id(ruleset_id)}/usage"
    response = await get_object(path)
    return {
        "object_id": str(ruleset_id),
        "source": "compliance_ruleset_usage",
        "data": response.get("data", response),
    }


def _ruleset_relation_props(relation: str, include_var_value: bool) -> str | None:
    if relation == "variables":
        return _ruleset_variable_props(include_var_value)
    if relation in {"nodes", "candidate_nodes"}:
        return NODE_RELATION_PROPS
    if relation in {"services", "candidate_services"}:
        return SERVICE_RELATION_PROPS
    return None


def _ruleset_variable_props(include_var_value: bool) -> str:
    if include_var_value:
        return f"{RULESET_VARIABLE_PROPS},{RULESET_VARIABLE_VALUE_PROP}"
    return RULESET_VARIABLE_PROPS

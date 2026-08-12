from typing import Any, Literal

from ._common import (
    NODE_RELATION_PROPS,
    SERVICE_RELATION_PROPS,
    get_collection_page,
    parse_filters,
    quote_path_id,
    relation_response,
)
from ._ruleset import ruleset_variable_props
from .rulesets import _resolve_ruleset_identity


RulesetRelation = Literal[
    "variables",
    "nodes",
    "services",
    "candidate_nodes",
    "candidate_services",
    "publications",
    "responsibles",
]


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
    return relation_response(
        response,
        "compliance_ruleset_items",
        ruleset_id,
        relation,
        parsed_filters,
        selected_props,
    )


async def get_compliance_ruleset_candidate_nodes(
    ruleset_id: int | str | None = None,
    ruleset_name: str | None = None,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "nodename",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    return await _get_compliance_ruleset_relation(
        relation="candidate_nodes",
        ruleset_id=ruleset_id,
        ruleset_name=ruleset_name,
        filters=filters,
        props=props,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )


async def get_compliance_ruleset_candidate_services(
    ruleset_id: int | str | None = None,
    ruleset_name: str | None = None,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "svcname",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    return await _get_compliance_ruleset_relation(
        relation="candidate_services",
        ruleset_id=ruleset_id,
        ruleset_name=ruleset_name,
        filters=filters,
        props=props,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )


async def get_compliance_ruleset_publications(
    ruleset_id: int | str | None = None,
    ruleset_name: str | None = None,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "role",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    return await _get_compliance_ruleset_relation(
        relation="publications",
        ruleset_id=ruleset_id,
        ruleset_name=ruleset_name,
        filters=filters,
        props=props,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )


async def get_compliance_ruleset_responsibles(
    ruleset_id: int | str | None = None,
    ruleset_name: str | None = None,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "role",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    return await _get_compliance_ruleset_relation(
        relation="responsibles",
        ruleset_id=ruleset_id,
        ruleset_name=ruleset_name,
        filters=filters,
        props=props,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )


async def _get_compliance_ruleset_relation(
    relation: RulesetRelation,
    ruleset_id: int | str | None = None,
    ruleset_name: str | None = None,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    resolved = await _resolve_ruleset_identity(
        ruleset_id=ruleset_id,
        ruleset_name=ruleset_name,
    )
    resolved_id = str(resolved["id"])
    resolved_name = resolved.get("ruleset_name")
    response = await get_compliance_ruleset_items(
        ruleset_id=resolved_id,
        relation=relation,
        filters=filters,
        props=props,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )
    response["ruleset_name"] = resolved_name
    return response


def _ruleset_relation_props(
    relation: str,
    include_var_value: bool,
) -> str | None:
    if relation == "variables":
        return ruleset_variable_props(include_var_value)
    if relation in {"nodes", "candidate_nodes"}:
        return NODE_RELATION_PROPS
    if relation in {"services", "candidate_services"}:
        return SERVICE_RELATION_PROPS
    return None

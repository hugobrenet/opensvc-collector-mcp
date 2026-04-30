from typing import Any, Literal

from ._common import (
    get_collection_page,
    get_object,
    parse_filters,
    quote_path_id,
)

MODULESET_PROPS = "id,modset_name,modset_author,modset_updated"
RULESET_PROPS = "id,ruleset_name,ruleset_type,ruleset_public"
MODULE_PROPS = (
    "id,modset_id,modset_mod_name,autofix,modset_mod_author,modset_mod_updated"
)
RULESET_VARIABLE_PROPS = "id,ruleset_id,var_name,var_class,var_author,var_updated"
RULESET_VARIABLE_VALUE_PROP = "var_value"
NODE_RELATION_PROPS = "node_id,nodename,app,node_env,status,updated"
SERVICE_RELATION_PROPS = (
    "svc_id,svcname,svc_app,svc_env,svc_status,svc_availstatus,updated"
)

ModulesetRelation = Literal[
    "modules",
    "nodes",
    "services",
    "candidate_nodes",
    "candidate_services",
    "publications",
    "responsibles",
]
RulesetRelation = Literal[
    "variables",
    "nodes",
    "services",
    "candidate_nodes",
    "candidate_services",
    "publications",
    "responsibles",
]


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
    return _collection_response(response, "compliance_modulesets", parsed_filters, selected_props)


async def get_compliance_moduleset(
    moduleset_id: int | str,
    props: str | None = None,
) -> dict[str, Any]:
    selected_props = props or MODULESET_PROPS
    path = f"/compliance/modulesets/{quote_path_id(moduleset_id)}"
    response = await get_object(path, props=selected_props)
    return _object_response(response, "compliance_moduleset", moduleset_id, selected_props)


async def get_compliance_moduleset_items(
    moduleset_id: int | str,
    relation: ModulesetRelation,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    selected_props = props or _moduleset_relation_props(relation)
    parsed_filters = parse_filters(filters)
    path = f"/compliance/modulesets/{quote_path_id(moduleset_id)}/{relation}"
    response = await get_collection_page(
        path,
        filters=parsed_filters,
        props=selected_props,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )
    return _relation_response(
        response,
        "compliance_moduleset_items",
        moduleset_id,
        relation,
        parsed_filters,
        selected_props,
    )


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
    data = _object_response(response, "compliance_moduleset_module", module_id, selected_props)
    data["moduleset_id"] = str(moduleset_id)
    return data


async def get_compliance_moduleset_usage(moduleset_id: int | str) -> dict[str, Any]:
    path = f"/compliance/modulesets/{quote_path_id(moduleset_id)}/usage"
    response = await get_object(path)
    return {
        "object_id": str(moduleset_id),
        "source": "compliance_moduleset_usage",
        "data": response.get("data", response),
    }


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
    return _collection_response(response, "compliance_rulesets", parsed_filters, selected_props)


async def get_compliance_ruleset(
    ruleset_id: int | str,
    props: str | None = None,
) -> dict[str, Any]:
    selected_props = props or RULESET_PROPS
    path = f"/compliance/rulesets/{quote_path_id(ruleset_id)}"
    response = await get_object(path, props=selected_props)
    return _object_response(response, "compliance_ruleset", ruleset_id, selected_props)


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
    return _relation_response(
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
    data = _object_response(response, "compliance_ruleset_variable", variable_id, selected_props)
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


def _moduleset_relation_props(relation: str) -> str | None:
    if relation == "modules":
        return MODULE_PROPS
    if relation in {"nodes", "candidate_nodes"}:
        return NODE_RELATION_PROPS
    if relation in {"services", "candidate_services"}:
        return SERVICE_RELATION_PROPS
    return None


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


def _collection_response(
    response: dict[str, Any],
    source: str,
    filters: list[tuple[str, str]],
    props: str | None,
) -> dict[str, Any]:
    rows = response.get("data", [])
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": source,
            "filter": {field: value for field, value in filters},
            "included_props": props.split(",") if props else meta.get("included_props", []),
            "output_count": len(rows),
        }
    )
    return {"meta": meta, "data": rows}


def _object_response(
    response: dict[str, Any],
    source: str,
    object_id: int | str,
    props: str | None,
) -> dict[str, Any]:
    rows = response.get("data", [])
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": source,
            "object_id": str(object_id),
            "included_props": props.split(",") if props else meta.get("included_props", []),
            "output_count": len(rows),
        }
    )
    return {"object_id": str(object_id), "meta": meta, "data": rows}


def _relation_response(
    response: dict[str, Any],
    source: str,
    object_id: int | str,
    relation: str,
    filters: list[tuple[str, str]],
    props: str | None,
) -> dict[str, Any]:
    data = _collection_response(response, source, filters, props)
    data["object_id"] = str(object_id)
    data["relation"] = relation
    data["meta"].update({"object_id": str(object_id), "relation": relation})
    return data

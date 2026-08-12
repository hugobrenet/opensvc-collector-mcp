from typing import Any, Literal

from ._common import (
    NODE_RELATION_PROPS,
    SERVICE_RELATION_PROPS,
    get_collection_page,
    parse_filters,
    quote_path_id,
    relation_response,
)
from .modulesets import MODULE_PROPS, _resolve_moduleset_identity


ModulesetRelation = Literal[
    "modules",
    "nodes",
    "services",
    "candidate_nodes",
    "candidate_services",
    "publications",
    "responsibles",
]


async def get_compliance_moduleset_items(
    moduleset_id: int | str | None,
    relation: ModulesetRelation,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
    modset_name: str | None = None,
) -> dict[str, Any]:
    resolved = await _resolve_moduleset_identity(
        moduleset_id=moduleset_id,
        modset_name=modset_name,
    )
    resolved_id = str(resolved["id"])
    resolved_name = resolved.get("modset_name")
    selected_props = props or _moduleset_relation_props(relation)
    parsed_filters = parse_filters(filters)
    path = f"/compliance/modulesets/{quote_path_id(resolved_id)}/{relation}"
    response = await get_collection_page(
        path,
        filters=parsed_filters,
        props=selected_props,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )
    data = relation_response(
        response,
        "compliance_moduleset_items",
        resolved_id,
        relation,
        parsed_filters,
        selected_props,
    )
    data["modset_name"] = resolved_name
    return data


async def get_compliance_moduleset_modules(
    moduleset_id: int | str | None = None,
    modset_name: str | None = None,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    return await get_compliance_moduleset_items(
        moduleset_id=moduleset_id,
        modset_name=modset_name,
        relation="modules",
        filters=filters,
        props=props,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )


async def get_compliance_moduleset_nodes(
    moduleset_id: int | str | None = None,
    modset_name: str | None = None,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    return await get_compliance_moduleset_items(
        moduleset_id=moduleset_id,
        modset_name=modset_name,
        relation="nodes",
        filters=filters,
        props=props,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )


async def get_compliance_moduleset_candidate_nodes(
    moduleset_id: int | str | None = None,
    modset_name: str | None = None,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    return await get_compliance_moduleset_items(
        moduleset_id=moduleset_id,
        modset_name=modset_name,
        relation="candidate_nodes",
        filters=filters,
        props=props,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )


async def get_compliance_moduleset_services(
    moduleset_id: int | str | None = None,
    modset_name: str | None = None,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    return await get_compliance_moduleset_items(
        moduleset_id=moduleset_id,
        modset_name=modset_name,
        relation="services",
        filters=filters,
        props=props,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )


async def get_compliance_moduleset_candidate_services(
    moduleset_id: int | str | None = None,
    modset_name: str | None = None,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    return await get_compliance_moduleset_items(
        moduleset_id=moduleset_id,
        modset_name=modset_name,
        relation="candidate_services",
        filters=filters,
        props=props,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )


async def get_compliance_moduleset_publications(
    moduleset_id: int | str | None = None,
    modset_name: str | None = None,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    return await get_compliance_moduleset_items(
        moduleset_id=moduleset_id,
        modset_name=modset_name,
        relation="publications",
        filters=filters,
        props=props,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )


async def get_compliance_moduleset_responsibles(
    moduleset_id: int | str | None = None,
    modset_name: str | None = None,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    return await get_compliance_moduleset_items(
        moduleset_id=moduleset_id,
        modset_name=modset_name,
        relation="responsibles",
        filters=filters,
        props=props,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )


def _moduleset_relation_props(relation: str) -> str | None:
    if relation == "modules":
        return MODULE_PROPS
    if relation in {"nodes", "candidate_nodes"}:
        return NODE_RELATION_PROPS
    if relation in {"services", "candidate_services"}:
        return SERVICE_RELATION_PROPS
    return None

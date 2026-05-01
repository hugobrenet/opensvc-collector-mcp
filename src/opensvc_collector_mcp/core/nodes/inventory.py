from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get, collector_get_all


DEFAULT_SEARCH_NODE_PROPS = (
    "nodename,status,asset_env,node_env,loc_city,loc_country,"
    "app,team_responsible,os_name"
)


async def list_nodes(props: str | None = None) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if props:
        params["props"] = props
    return await collector_get_all("/nodes", params=params or None)


async def list_node_props() -> dict[str, Any]:
    response = await collector_get("/nodes", params={"props": "nodename"})
    available_props = response.get("meta", {}).get("available_props", [])
    node_props = [
        prop.removeprefix("nodes.") for prop in available_props if isinstance(prop, str)
    ]

    return {
        "count": len(available_props),
        "available_props": available_props,
        "node_props": node_props,
    }


async def search_nodes(
    filters: dict[str, str] | str | None = None,
    nodename_contains: str | None = None,
    status: str | None = None,
    asset_env: str | None = None,
    node_env: str | None = None,
    loc_city: str | None = None,
    loc_country: str | None = None,
    team_responsible: str | None = None,
    app: str | None = None,
    os_name: str | None = None,
    props: str | None = None,
    limit: int = 20,
    offset: int = 0,
    max_scan: int = 5000,
) -> dict[str, Any]:
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    max_scan = max(limit + offset, min(max_scan, 50000))
    selected_props = _props_with_required(
        props or DEFAULT_SEARCH_NODE_PROPS, "nodename"
    )
    parsed_filters = _node_search_filters(
        filters,
        status=status,
        asset_env=asset_env,
        node_env=node_env,
        loc_city=loc_city,
        loc_country=loc_country,
        team_responsible=team_responsible,
        app=app,
        os_name=os_name,
    )

    if not nodename_contains:
        params = _node_search_params(
            filters=parsed_filters,
            props=selected_props,
            limit=limit,
            offset=offset,
        )
        return await collector_get("/nodes", params=params)

    needle = nodename_contains.strip().lower()
    if not needle:
        raise ValueError("nodename_contains must not be empty")

    matches: list[dict[str, Any]] = []
    scanned = 0
    api_offset = 0
    page_size = min(max(limit + offset, 100), 1000)
    total_candidates: int | None = None

    while scanned < max_scan:
        response = await collector_get(
            "/nodes",
            params=_node_search_params(
                filters=parsed_filters,
                props=selected_props,
                limit=min(page_size, max_scan - scanned),
                offset=api_offset,
            ),
        )
        meta = response.get("meta", {})
        data = response.get("data", [])
        if total_candidates is None:
            total_candidates = meta.get("total")

        for node in data:
            nodename = str(node.get("nodename", "")).lower()
            if needle in nodename:
                matches.append(node)

        count = len(data)
        scanned += count
        api_offset += count
        if count == 0 or count < page_size or len(matches) >= offset + limit:
            break

    result_data = matches[offset : offset + limit]
    complete = total_candidates is None or api_offset >= total_candidates
    return {
        "meta": {
            "count": len(result_data),
            "total": len(matches) if complete else None,
            "limit": limit,
            "offset": offset,
            "scanned": scanned,
            "max_scan": max_scan,
            "complete": complete,
            "filters": {
                "nodename_contains": nodename_contains,
                **{field: value for field, value in parsed_filters},
            },
            "included_props": selected_props.split(","),
        },
        "data": result_data,
    }


async def count_nodes(
    filters: dict[str, str] | str | None = None,
    status: str | None = None,
    asset_env: str | None = None,
    node_env: str | None = None,
    loc_city: str | None = None,
    loc_country: str | None = None,
    team_responsible: str | None = None,
    app: str | None = None,
    os_name: str | None = None,
) -> dict[str, Any]:
    parsed_filters = _node_search_filters(
        filters,
        status=status,
        asset_env=asset_env,
        node_env=node_env,
        loc_city=loc_city,
        loc_country=loc_country,
        team_responsible=team_responsible,
        app=app,
        os_name=os_name,
    )
    response = await collector_get(
        "/nodes",
        params=_node_search_params(
            filters=parsed_filters,
            props="nodename",
            limit=1,
            offset=0,
        ),
    )
    meta = response.get("meta", {})
    return {
        "count": meta.get("total"),
        "filters": {field: value for field, value in parsed_filters},
    }


async def get_node(nodename: str) -> dict[str, Any]:
    nodename = nodename.strip()
    if not nodename:
        raise ValueError("nodename must not be empty")

    return await collector_get(f"/nodes/{quote(nodename, safe='')}")


def _props_with_required(props: str, *required_props: str) -> str:
    selected = [prop.strip() for prop in props.split(",") if prop.strip()]
    for prop in required_props:
        if prop not in selected:
            selected.append(prop)
    return ",".join(selected)


def _node_search_filters(
    raw_filters: dict[str, str] | str | None = None,
    **criteria: str | None,
) -> list[tuple[str, str]]:
    filters: list[tuple[str, str]] = []
    filters.extend(_parse_node_filters(raw_filters))
    for field, value in criteria.items():
        if value is None:
            continue
        value = value.strip()
        if value:
            filters.append((field, value))
    return filters


def _parse_node_filters(
    raw_filters: dict[str, str] | str | None,
) -> list[tuple[str, str]]:
    if not raw_filters:
        return []
    if isinstance(raw_filters, dict):
        return [
            (field.strip(), value.strip())
            for field, value in raw_filters.items()
            if field.strip() and value.strip()
        ]

    filters: list[tuple[str, str]] = []
    for item in raw_filters.split(","):
        item = item.strip()
        if not item:
            continue
        if "=" not in item:
            raise ValueError("filters must use the format 'prop=value,prop=value'")
        field, value = item.split("=", 1)
        field = field.strip()
        value = value.strip()
        if not field or not value:
            raise ValueError("filters must not contain empty props or values")
        filters.append((field, value))
    return filters


def _node_search_params(
    filters: list[tuple[str, str]],
    props: str,
    limit: int,
    offset: int,
) -> list[tuple[str, Any]]:
    params: list[tuple[str, Any]] = [
        ("props", props),
        ("limit", limit),
        ("offset", offset),
    ]
    for field, value in filters:
        params.append(("filters", f"{field}={value}"))
    return params

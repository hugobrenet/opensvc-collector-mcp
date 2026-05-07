from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get
from opensvc_collector_mcp.core.utils import collection_params

from ._common import _parse_service_filters


SERVICE_TAGS_PROPS = (
    "tags.tag_name,tags.tag_id,tags.tag_data,tags.tag_exclude,tags.tag_created"
)
async def get_service_tags(
    svcname: str,
    filters: dict[str, str] | str | None = None,
    tag_name: str | None = None,
    tag_id: str | None = None,
    tag_exclude: str | None = None,
    props: str | None = None,
    orderby: str | None = "tags.tag_name",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    selected_props = props or SERVICE_TAGS_PROPS
    parsed_filters = _service_tag_filters(
        filters,
        tag_name=tag_name,
        tag_id=tag_id,
        tag_exclude=tag_exclude,
    )
    response = await collector_get(
        f"/services/{quote(svcname, safe='')}/tags",
        params=_service_tag_params(
            filters=parsed_filters,
            props=selected_props,
            orderby=orderby,
            search=search,
            limit=limit,
            offset=offset,
        ),
    )
    rows = response.get("data", [])
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "service_tags",
            "filter": {
                "svcname": svcname,
                **{field: value for field, value in parsed_filters},
            },
            "included_props": selected_props.split(","),
            "output_count": len(rows),
        }
    )
    return {
        "svcname": svcname,
        "meta": meta,
        "data": rows,
    }


def _service_tag_filters(
    raw_filters: dict[str, str] | str | None = None,
    **criteria: str | None,
) -> list[tuple[str, str]]:
    filters = [
        (_service_tag_filter_field(field), value)
        for field, value in _parse_service_filters(raw_filters)
    ]
    for field, value in criteria.items():
        if value is None:
            continue
        value = value.strip()
        if value:
            filters.append((_service_tag_filter_field(field), value))
    return filters


def _service_tag_filter_field(field: str) -> str:
    if "." in field:
        return field
    return {
        "tag_name": "tags.tag_name",
        "tag_id": "tags.tag_id",
        "tag_data": "tags.tag_data",
        "tag_exclude": "tags.tag_exclude",
        "tag_created": "tags.tag_created",
    }.get(field, field)


def _service_tag_params(
    filters: list[tuple[str, str]],
    props: str,
    orderby: str | None,
    search: str | None,
    limit: int,
    offset: int,
) -> list[tuple[str, Any]]:
    return collection_params(
        filters=filters,
        props=props,
        orderby=orderby,
        search=search,
        limit=limit,
        offset=offset,
    )

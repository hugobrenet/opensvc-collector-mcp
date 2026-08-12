from typing import Any

from opensvc_collector_mcp.client import collector_get, collector_get_page
from opensvc_collector_mcp.core.utils import collection_params, parse_collector_filters

from ._common import quote_selector, require_selector


DEFAULT_ARRAY_DISKGROUP_QUOTA_PROPS = "id,dg_id,app_id,quota"


async def get_array_diskgroup_quotas(
    array: str,
    diskgroup: str,
    filters: dict[str, str] | str | None = None,
    props: str | None = None,
    orderby: str | None = "id",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    selector = require_selector(array, "array")
    diskgroup_selector = require_selector(diskgroup, "diskgroup")
    selected_props = props or DEFAULT_ARRAY_DISKGROUP_QUOTA_PROPS
    response = await collector_get_page(
        (
            f"/arrays/{quote_selector(selector)}/diskgroups/"
            f"{quote_selector(diskgroup_selector)}/quotas"
        ),
        params=collection_params(
            filters=parse_collector_filters(filters),
            props=selected_props,
            orderby=orderby,
            search=search,
            limit=limit,
            offset=offset,
        ),
    )
    return {
        "array": selector,
        "diskgroup": diskgroup_selector,
        **response,
    }


async def get_array_diskgroup_quota(
    array: str,
    diskgroup: str,
    quota: str,
    props: str | None = None,
) -> dict[str, Any]:
    selector = require_selector(array, "array")
    diskgroup_selector = require_selector(diskgroup, "diskgroup")
    quota_selector = require_selector(quota, "quota")
    params = {"props": props} if props else None
    response = await collector_get(
        (
            f"/arrays/{quote_selector(selector)}/diskgroups/"
            f"{quote_selector(diskgroup_selector)}/quotas/"
            f"{quote_selector(quota_selector)}"
        ),
        params=params,
    )
    rows = response.get("data", [])
    meta = dict(response.get("meta") or {})
    meta.update(
        {
            "source": "arrays/<id>/diskgroups/<id>/quotas/<id>",
            "selector": selector,
            "diskgroup_selector": diskgroup_selector,
            "quota_selector": quota_selector,
            "count": len(rows) if isinstance(rows, list) else 0,
        }
    )
    return {
        "array": selector,
        "diskgroup": diskgroup_selector,
        "quota": quota_selector,
        "meta": meta,
        "data": rows if isinstance(rows, list) else [],
    }

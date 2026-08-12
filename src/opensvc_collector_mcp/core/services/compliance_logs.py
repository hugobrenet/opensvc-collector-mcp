from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get_page

from ._common import _parse_service_filters
from ._compliance import select_compliance_props, shape_compliance_response


async def get_service_compliance_logs(
    svcname: str,
    filters: dict[str, str] | str | None = None,
    run_module: str | None = None,
    run_status: int | str | None = None,
    run_action: str | None = None,
    node_id: str | None = None,
    rset_md5: str | None = None,
    props: str | None = None,
    orderby: str | None = "~run_date",
    limit: int = 20,
    offset: int = 0,
    include_run_log: bool = False,
    include_run_log_preview: bool = True,
    run_log_max_chars: int = 1000,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    run_log_max_chars = max(0, min(run_log_max_chars, 20000))
    selected_props = select_compliance_props(
        props,
        include_run_log=include_run_log,
        include_run_log_preview=include_run_log_preview,
    )
    parsed_filters = _service_compliance_log_filters(
        filters,
        run_module=run_module,
        run_status=str(run_status) if run_status is not None else None,
        run_action=run_action,
        node_id=node_id,
        rset_md5=rset_md5,
    )
    response = await collector_get_page(
        f"/services/{quote(svcname, safe='')}/compliance/logs",
        params=_service_compliance_log_params(
            filters=parsed_filters,
            props=selected_props,
            orderby=orderby,
            limit=limit,
            offset=offset,
        ),
    )
    return await shape_compliance_response(
        svcname=svcname,
        response=response,
        include_run_log=include_run_log,
        include_run_log_preview=include_run_log_preview,
        run_log_max_chars=run_log_max_chars,
    )


def _service_compliance_log_filters(
    raw_filters: dict[str, str] | str | None = None,
    **criteria: str | None,
) -> list[tuple[str, str]]:
    filters = [
        (_service_compliance_log_filter_field(field), value)
        for field, value in _parse_service_filters(raw_filters)
    ]
    for field, value in criteria.items():
        if value is None:
            continue
        value = value.strip()
        if value:
            filters.append((_service_compliance_log_filter_field(field), value))
    return filters


def _service_compliance_log_filter_field(field: str) -> str:
    if "." in field:
        return field
    return {
        "id": "comp_log.id",
        "svc_id": "comp_log.svc_id",
        "node_id": "comp_log.node_id",
        "run_module": "comp_log.run_module",
        "run_action": "comp_log.run_action",
        "run_status": "comp_log.run_status",
        "run_date": "comp_log.run_date",
        "run_log": "comp_log.run_log",
        "rset_md5": "comp_log.rset_md5",
    }.get(field, field)


def _service_compliance_log_params(
    filters: list[tuple[str, str]],
    props: str,
    orderby: str | None,
    limit: int,
    offset: int,
) -> list[tuple[str, Any]]:
    params: list[tuple[str, Any]] = [
        ("props", props),
        ("limit", limit),
        ("offset", offset),
    ]
    if orderby:
        params.append(("orderby", orderby))
    for field, value in filters:
        params.append(("filters", f"{field}={value}"))
    return params

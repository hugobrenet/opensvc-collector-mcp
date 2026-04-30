from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get_all
from opensvc_collector_mcp.core.utils import (
    enrich_rows_with_nodenames,
    get_nodenames_by_node_ids,
)

from ._common import (
    _ensure_props_include,
    _int_or_none,
    _parse_service_filters,
    _truncate_text,
    _unresolved_node_ids,
)


SERVICE_COMPLIANCE_STATUS_PROPS = (
    "svc_id,node_id,run_module,run_action,run_status,run_date,rset_md5,id"
)
SERVICE_COMPLIANCE_RUN_LOG_PROP = "run_log"


async def get_service_compliance_status(
    svcname: str,
    filters: dict[str, str] | str | None = None,
    run_module: str | None = None,
    run_status: int | str | None = None,
    run_action: str | None = None,
    node_id: str | None = None,
    rset_md5: str | None = None,
    props: str | None = None,
    page_size: int = 1000,
    max_status: int = 10000,
    include_run_log: bool = False,
    include_run_log_preview: bool = True,
    run_log_max_chars: int = 1000,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    run_log_max_chars = max(0, min(run_log_max_chars, 20000))
    selected_props = props or SERVICE_COMPLIANCE_STATUS_PROPS
    if include_run_log or include_run_log_preview:
        selected_props = _ensure_props_include(
            selected_props,
            SERVICE_COMPLIANCE_RUN_LOG_PROP,
        )
    parsed_filters = _service_compliance_status_filters(
        filters,
        run_module=run_module,
        run_status=str(run_status) if run_status is not None else None,
        run_action=run_action,
        node_id=node_id,
        rset_md5=rset_md5,
    )
    response = await collector_get_all(
        f"/services/{quote(svcname, safe='')}/compliance/status",
        params=_service_compliance_status_params(
            filters=parsed_filters,
            props=selected_props,
        ),
        strategy="paged",
        page_size=page_size,
        max_items=max_status,
    )
    raw_rows = response.get("data", [])
    nodenames_by_node_id = await get_nodenames_by_node_ids(
        str(row.get("node_id") or "") for row in raw_rows
    )
    enriched_rows = enrich_rows_with_nodenames(raw_rows, nodenames_by_node_id)
    rows = _service_compliance_status_rows(
        enriched_rows,
        include_run_log=include_run_log,
        include_run_log_preview=include_run_log_preview,
        run_log_max_chars=run_log_max_chars,
    )
    unresolved_node_ids = _unresolved_node_ids(rows, nodenames_by_node_id)
    summary = _service_compliance_status_summary(rows)
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "service_compliance_status",
            "filter": {
                "svcname": svcname,
                **{field: value for field, value in parsed_filters},
            },
            "included_props": selected_props.split(","),
            "include_run_log": include_run_log,
            "include_run_log_preview": include_run_log_preview,
            "run_log_max_chars": run_log_max_chars,
            "status_count": len(rows),
            "node_names_resolved": not unresolved_node_ids,
            "node_name_count": len(nodenames_by_node_id),
            "unresolved_node_ids": unresolved_node_ids,
            **summary,
        }
    )
    return {
        "svcname": svcname,
        "meta": meta,
        "data": rows,
    }


def _service_compliance_status_filters(
    raw_filters: dict[str, str] | str | None = None,
    **criteria: str | None,
) -> list[tuple[str, str]]:
    filters = [
        (_service_compliance_status_filter_field(field), value)
        for field, value in _parse_service_filters(raw_filters)
    ]
    for field, value in criteria.items():
        if value is None:
            continue
        value = value.strip()
        if value:
            filters.append((_service_compliance_status_filter_field(field), value))
    return filters


def _service_compliance_status_filter_field(field: str) -> str:
    if "." in field:
        return field
    return {
        "id": "comp_status.id",
        "svc_id": "comp_status.svc_id",
        "node_id": "comp_status.node_id",
        "run_module": "comp_status.run_module",
        "run_action": "comp_status.run_action",
        "run_status": "comp_status.run_status",
        "run_date": "comp_status.run_date",
        "run_log": "comp_status.run_log",
        "rset_md5": "comp_status.rset_md5",
    }.get(field, field)


def _service_compliance_status_params(
    filters: list[tuple[str, str]],
    props: str,
) -> list[tuple[str, Any]]:
    params: list[tuple[str, Any]] = [("props", props)]
    for field, value in filters:
        params.append(("filters", f"{field}={value}"))
    return params


def _service_compliance_status_rows(
    rows: list[dict[str, Any]],
    include_run_log: bool,
    include_run_log_preview: bool,
    run_log_max_chars: int,
) -> list[dict[str, Any]]:
    shaped: list[dict[str, Any]] = []
    for row in rows:
        status = dict(row)
        run_log = status.get(SERVICE_COMPLIANCE_RUN_LOG_PROP)
        if run_log is not None and include_run_log_preview:
            text = str(run_log)
            status["run_log_preview"] = _truncate_text(text, run_log_max_chars)
            status["run_log_truncated"] = len(text) > run_log_max_chars
        if not include_run_log:
            status.pop(SERVICE_COMPLIANCE_RUN_LOG_PROP, None)
        shaped.append(status)
    return shaped


def _service_compliance_status_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ok_count = 0
    error_count = 0
    unknown_count = 0
    failed_modules: list[str] = []
    for row in rows:
        status = _int_or_none(row.get("run_status"))
        if status == 0:
            ok_count += 1
            continue
        if status is None:
            unknown_count += 1
            continue
        error_count += 1
        run_module = row.get("run_module")
        if run_module and str(run_module) not in failed_modules:
            failed_modules.append(str(run_module))
    return {
        "ok_count": ok_count,
        "error_count": error_count,
        "unknown_count": unknown_count,
        "failed_modules": failed_modules,
    }

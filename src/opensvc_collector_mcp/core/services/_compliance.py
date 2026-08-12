from typing import Any

from opensvc_collector_mcp.core.utils import (
    enrich_rows_with_nodenames,
    get_nodenames_by_node_ids,
)

from ._common import (
    _ensure_props_include,
    _int_or_none,
    _truncate_text,
    _unresolved_node_ids,
)


SERVICE_COMPLIANCE_PROPS = (
    "svc_id,node_id,run_module,run_action,run_status,run_date,rset_md5,id"
)
SERVICE_COMPLIANCE_RUN_LOG_PROP = "run_log"


def select_compliance_props(
    props: str | None,
    *,
    include_run_log: bool,
    include_run_log_preview: bool,
) -> str:
    selected_props = props or SERVICE_COMPLIANCE_PROPS
    if include_run_log or include_run_log_preview:
        selected_props = _ensure_props_include(
            selected_props,
            SERVICE_COMPLIANCE_RUN_LOG_PROP,
        )
    return selected_props


async def shape_compliance_response(
    *,
    svcname: str,
    response: dict[str, Any],
    include_run_log: bool,
    include_run_log_preview: bool,
    run_log_max_chars: int,
) -> dict[str, Any]:
    raw_rows = response.get("data", [])
    nodenames_by_node_id = await get_nodenames_by_node_ids(
        str(row.get("node_id") or "") for row in raw_rows
    )
    enriched_rows = enrich_rows_with_nodenames(raw_rows, nodenames_by_node_id)
    rows = _service_compliance_rows(
        enriched_rows,
        include_run_log=include_run_log,
        include_run_log_preview=include_run_log_preview,
        run_log_max_chars=run_log_max_chars,
    )
    unresolved_node_ids = _unresolved_node_ids(rows, nodenames_by_node_id)
    summary = _service_compliance_summary(rows)
    return {
        "svcname": svcname,
        "pagination": response["pagination"],
        "summary": {
            "node_names_resolved": not unresolved_node_ids,
            "node_name_count": len(nodenames_by_node_id),
            "unresolved_node_ids": unresolved_node_ids,
            **summary,
        },
        "data": rows,
    }


def _service_compliance_rows(
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


def _service_compliance_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
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

from typing import Any, Literal

from opensvc_collector_mcp.client import collector_get
from opensvc_collector_mcp.core.utils import (
    enrich_rows_with_nodenames,
    enrich_rows_with_svcnames,
    get_nodenames_by_node_ids,
    get_svcnames_by_svc_ids,
)

from ._common import (
    collection_params,
    ensure_props_include,
    int_or_none,
    parse_filters,
    quote_path_id,
    truncate_text,
)

COMPLIANCE_STATUS_PROPS = (
    "services.svcname:svcname,nodes.nodename:nodename,"
    "svc_id,node_id,run_module,run_action,run_status,run_date,rset_md5,id"
)
COMPLIANCE_LOG_PROPS = (
    "svc_id,node_id,run_module,run_action,run_status,run_date,rset_md5,id"
)
COMPLIANCE_RUN_LOG_PROP = "run_log"
RunSource = Literal["status", "logs"]


async def get_compliance_status(
    filters: dict[str, str] | str | None = None,
    run_module: str | None = None,
    run_status: int | str | None = None,
    run_action: str | None = None,
    node_id: str | None = None,
    svc_id: str | None = None,
    rset_md5: str | None = None,
    props: str | None = None,
    limit: int = 50,
    offset: int = 0,
    latest: bool = True,
    latest_first: bool = True,
    include_run_log: bool = False,
    include_run_log_preview: bool = False,
    run_log_max_chars: int = 1000,
) -> dict[str, Any]:
    return await _get_compliance_runs(
        source="status",
        filters=filters,
        run_module=run_module,
        run_status=run_status,
        run_action=run_action,
        node_id=node_id,
        svc_id=svc_id,
        rset_md5=rset_md5,
        props=props,
        limit=limit,
        offset=offset,
        latest=latest,
        latest_first=latest_first,
        include_run_log=include_run_log,
        include_run_log_preview=include_run_log_preview,
        run_log_max_chars=run_log_max_chars,
    )


async def get_compliance_logs(
    filters: dict[str, str] | str | None = None,
    run_module: str | None = None,
    run_status: int | str | None = None,
    run_action: str | None = None,
    node_id: str | None = None,
    svc_id: str | None = None,
    rset_md5: str | None = None,
    props: str | None = None,
    limit: int = 20,
    offset: int = 0,
    latest: bool = True,
    latest_first: bool = True,
    include_run_log: bool = False,
    include_run_log_preview: bool = True,
    run_log_max_chars: int = 1000,
) -> dict[str, Any]:
    return await _get_compliance_runs(
        source="logs",
        filters=filters,
        run_module=run_module,
        run_status=run_status,
        run_action=run_action,
        node_id=node_id,
        svc_id=svc_id,
        rset_md5=rset_md5,
        props=props,
        limit=limit,
        offset=offset,
        latest=latest,
        latest_first=latest_first,
        include_run_log=include_run_log,
        include_run_log_preview=include_run_log_preview,
        run_log_max_chars=run_log_max_chars,
    )


async def get_compliance_run_detail(
    source: RunSource,
    run_id: int | str,
    props: str | None = None,
    include_run_log: bool = False,
    include_run_log_preview: bool = True,
    run_log_max_chars: int = 2000,
) -> dict[str, Any]:
    run_log_max_chars = max(0, min(run_log_max_chars, 20000))
    selected_props = props or _default_run_props(source)
    if include_run_log or include_run_log_preview:
        selected_props = ensure_props_include(selected_props, COMPLIANCE_RUN_LOG_PROP)
    endpoint = f"/compliance/{source}/{quote_path_id(run_id)}"
    response = await collector_get(endpoint, params={"props": selected_props})
    rows = await _shape_run_rows(
        rows=response.get("data", []),
        include_run_log=include_run_log,
        include_run_log_preview=include_run_log_preview,
        run_log_max_chars=run_log_max_chars,
        enrich_names=True,
    )
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": f"compliance_{source}_detail",
            "run_id": str(run_id),
            "included_props": selected_props.split(","),
            "include_run_log": include_run_log,
            "include_run_log_preview": include_run_log_preview,
            "run_log_max_chars": run_log_max_chars,
            "output_count": len(rows),
        }
    )
    return {"run_id": str(run_id), "meta": meta, "data": rows}


async def _get_compliance_runs(
    source: RunSource,
    filters: dict[str, str] | str | None,
    run_module: str | None,
    run_status: int | str | None,
    run_action: str | None,
    node_id: str | None,
    svc_id: str | None,
    rset_md5: str | None,
    props: str | None,
    limit: int,
    offset: int,
    latest: bool,
    latest_first: bool,
    include_run_log: bool,
    include_run_log_preview: bool,
    run_log_max_chars: int,
) -> dict[str, Any]:
    limit = max(1, min(limit, 1000))
    offset = max(0, offset)
    run_log_max_chars = max(0, min(run_log_max_chars, 20000))
    selected_props = props or _default_run_props(source)
    if include_run_log or include_run_log_preview:
        selected_props = ensure_props_include(selected_props, COMPLIANCE_RUN_LOG_PROP)
    parsed_filters = _run_filters(
        source=source,
        raw_filters=filters,
        run_module=run_module,
        run_status=str(run_status) if run_status is not None else None,
        run_action=run_action,
        node_id=node_id,
        svc_id=svc_id,
        rset_md5=rset_md5,
    )
    effective_offset = 0 if latest else offset
    orderby = "~run_date" if latest or latest_first else "run_date"
    response = await collector_get(
        f"/compliance/{source}",
        params=collection_params(
            filters=parsed_filters,
            props=selected_props,
            orderby=orderby,
            search=None,
            limit=limit,
            offset=effective_offset,
        ),
    )
    rows = await _shape_run_rows(
        rows=response.get("data", []),
        include_run_log=include_run_log,
        include_run_log_preview=include_run_log_preview,
        run_log_max_chars=run_log_max_chars,
        enrich_names=True,
    )
    rows = _sort_run_rows(rows, latest_first=latest_first)
    summary = _run_summary(rows)
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": f"compliance_{source}",
            "filter": {field: value for field, value in parsed_filters},
            "included_props": selected_props.split(","),
            "requested_latest": latest,
            "latest_first": latest_first,
            "effective_offset": effective_offset,
            "include_run_log": include_run_log,
            "include_run_log_preview": include_run_log_preview,
            "run_log_max_chars": run_log_max_chars,
            "output_count": len(rows),
            **summary,
        }
    )
    return {"meta": meta, "data": rows}


def _default_run_props(source: RunSource) -> str:
    if source == "status":
        return COMPLIANCE_STATUS_PROPS
    return COMPLIANCE_LOG_PROPS


def _run_filters(
    source: RunSource,
    raw_filters: dict[str, str] | str | None = None,
    **criteria: str | None,
) -> list[tuple[str, str]]:
    filters = [
        (_run_filter_field(source, field), value)
        for field, value in parse_filters(raw_filters)
    ]
    for field, value in criteria.items():
        if value is None:
            continue
        value = value.strip()
        if value:
            filters.append((_run_filter_field(source, field), value))
    return filters


def _run_filter_field(source: RunSource, field: str) -> str:
    if "." in field:
        return field
    table = "comp_status" if source == "status" else "comp_log"
    return {
        "id": f"{table}.id",
        "svc_id": f"{table}.svc_id",
        "node_id": f"{table}.node_id",
        "run_module": f"{table}.run_module",
        "run_action": f"{table}.run_action",
        "run_status": f"{table}.run_status",
        "run_date": f"{table}.run_date",
        "run_log": f"{table}.run_log",
        "rset_md5": f"{table}.rset_md5",
    }.get(field, field)


async def _shape_run_rows(
    rows: list[dict[str, Any]],
    include_run_log: bool,
    include_run_log_preview: bool,
    run_log_max_chars: int,
    enrich_names: bool,
) -> list[dict[str, Any]]:
    shaped: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        run_log = item.get(COMPLIANCE_RUN_LOG_PROP)
        if run_log is not None and include_run_log_preview:
            text = str(run_log)
            item["run_log_preview"] = truncate_text(text, run_log_max_chars)
            item["run_log_truncated"] = len(text) > run_log_max_chars
        if not include_run_log:
            item.pop(COMPLIANCE_RUN_LOG_PROP, None)
        shaped.append(item)

    if not enrich_names:
        return shaped

    nodenames_by_node_id = await get_nodenames_by_node_ids(
        str(row.get("node_id") or "") for row in shaped if not row.get("nodename")
    )
    rows_with_nodes = enrich_rows_with_nodenames(shaped, nodenames_by_node_id)
    svcnames_by_svc_id = await get_svcnames_by_svc_ids(
        str(row.get("svc_id") or "") for row in rows_with_nodes if not row.get("svcname")
    )
    return enrich_rows_with_svcnames(rows_with_nodes, svcnames_by_svc_id)


def _sort_run_rows(rows: list[dict[str, Any]], latest_first: bool) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            str(row.get("run_date") or ""),
            str(row.get("id") or ""),
        ),
        reverse=latest_first,
    )


def _run_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ok_count = 0
    error_count = 0
    unknown_count = 0
    failed_modules: list[str] = []
    for row in rows:
        status = int_or_none(row.get("run_status"))
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

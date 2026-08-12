from typing import Any

from ._common import parse_filters
from ._runs import get_compliance_runs


async def get_compliance_logs(
    filters: dict[str, str] | str | None = None,
    run_module: str | None = None,
    run_status: int | str | None = None,
    run_action: str | None = None,
    node_id: str | None = None,
    svc_id: str | None = None,
    rset_md5: str | None = None,
    props: str | None = None,
    orderby: str | None = "~run_date",
    limit: int = 20,
    offset: int = 0,
    include_run_log: bool = False,
    include_run_log_preview: bool = True,
    run_log_max_chars: int = 1000,
) -> dict[str, Any]:
    if not _has_run_log_scope(filters=filters, node_id=node_id, svc_id=svc_id):
        raise ValueError(
            "get_compliance_logs requires node_id or svc_id to avoid slow global "
            "Collector /compliance/logs queries"
        )
    return await get_compliance_runs(
        source="logs",
        filters=filters,
        run_module=run_module,
        run_status=run_status,
        run_action=run_action,
        node_id=node_id,
        svc_id=svc_id,
        rset_md5=rset_md5,
        props=props,
        orderby=orderby,
        limit=limit,
        offset=offset,
        include_run_log=include_run_log,
        include_run_log_preview=include_run_log_preview,
        run_log_max_chars=run_log_max_chars,
    )


def _has_run_log_scope(
    filters: dict[str, str] | str | None,
    node_id: str | None,
    svc_id: str | None,
) -> bool:
    if node_id and node_id.strip():
        return True
    if svc_id and svc_id.strip():
        return True
    for field, _value in parse_filters(filters):
        if field.rsplit(".", 1)[-1] in {"node_id", "svc_id"}:
            return True
    return False

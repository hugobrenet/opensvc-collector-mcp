from typing import Any

from opensvc_collector_mcp.client import collector_get

from ._common import ensure_props_include, quote_path_id
from ._runs import (
    COMPLIANCE_RUN_LOG_PROP,
    RunSource,
    default_run_props,
    shape_run_rows,
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
    selected_props = props or default_run_props(source)
    if include_run_log or include_run_log_preview:
        selected_props = ensure_props_include(
            selected_props,
            COMPLIANCE_RUN_LOG_PROP,
        )
    endpoint = f"/compliance/{source}/{quote_path_id(run_id)}"
    response = await collector_get(endpoint, params={"props": selected_props})
    rows = await shape_run_rows(
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

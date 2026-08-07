from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get, collector_get_page

from ._common import _int_or_none, _parse_service_filters, _truncate_text


SERVICE_ACTIONS_PROPS = (
    "action,status,begin,end,time,ack,acked_by,acked_date,acked_comment,"
    "rid,subset,hostid,node_id"
)
SERVICE_ACTIONS_LOG_PROP = "status_log"


async def get_service_actions(
    svcname: str,
    filters: dict[str, str] | str | None = None,
    action: str | None = None,
    status: str | None = None,
    ack: str | None = None,
    rid: str | None = None,
    subset: str | None = None,
    limit: int = 20,
    offset: int = 0,
    latest: bool = True,
    latest_first: bool = True,
    include_status_log: bool = False,
    include_status_log_preview: bool = True,
    status_log_max_chars: int = 500,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    status_log_max_chars = max(0, min(status_log_max_chars, 5000))
    parsed_filters = _service_action_filters(
        filters,
        action=action,
        status=status,
        ack=ack,
        rid=rid,
        subset=subset,
    )
    endpoint = f"/services/{quote(svcname, safe='')}/actions"
    props = _service_action_props(
        include_status_log=include_status_log,
        include_status_log_preview=include_status_log_preview,
    )

    response = await _get_service_action_page(
        endpoint=endpoint,
        filters=parsed_filters,
        props=props,
        limit=limit,
        offset=offset,
        latest=latest,
    )
    rows = _service_action_rows(
        response.get("data", []),
        include_status_log=include_status_log,
        include_status_log_preview=include_status_log_preview,
        status_log_max_chars=status_log_max_chars,
        latest_first=latest_first,
    )
    return {
        "svcname": svcname,
        "pagination": response["pagination"],
        "data": rows,
    }


async def get_service_unacknowledged_errors(
    svcname: str,
    filters: dict[str, str] | str | None = None,
    action: str | None = None,
    rid: str | None = None,
    subset: str | None = None,
    limit: int = 20,
    offset: int = 0,
    latest: bool = True,
    latest_first: bool = True,
    include_status_log: bool = False,
    include_status_log_preview: bool = True,
    status_log_max_chars: int = 500,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    status_log_max_chars = max(0, min(status_log_max_chars, 5000))
    parsed_filters = _service_unacknowledged_error_filters(
        filters,
        action=action,
        rid=rid,
        subset=subset,
    )
    endpoint = f"/services/{quote(svcname, safe='')}/actions_unacknowledged_errors"
    props = _service_action_props(
        include_status_log=include_status_log,
        include_status_log_preview=include_status_log_preview,
    )

    response = await _get_service_action_page(
        endpoint=endpoint,
        filters=parsed_filters,
        props=props,
        limit=limit,
        offset=offset,
        latest=latest,
    )
    rows = _service_action_rows(
        response.get("data", []),
        include_status_log=include_status_log,
        include_status_log_preview=include_status_log_preview,
        status_log_max_chars=status_log_max_chars,
        latest_first=latest_first,
    )
    return {
        "svcname": svcname,
        "pagination": response["pagination"],
        "data": rows,
    }


async def _get_service_action_page(
    endpoint: str,
    filters: list[tuple[str, str]],
    props: str,
    limit: int,
    offset: int,
    latest: bool,
) -> dict[str, Any]:
    if not latest:
        return await collector_get_page(
            endpoint,
            params=_service_action_params(
                filters=filters,
                props=props,
                limit=limit,
                offset=offset,
            ),
        )

    probe = await collector_get(
        endpoint,
        params=_service_action_params(
            filters=filters,
            props="action",
            limit=1,
            offset=0,
        ),
    )
    total = _int_or_none(probe.get("meta", {}).get("total"))
    if total is None:
        return await collector_get_page(
            endpoint,
            params=_service_action_params(
                filters=filters,
                props=props,
                limit=limit,
                offset=offset,
            ),
        )

    available = max(total - offset, 0)
    if available == 0:
        return {
            "pagination": {
                "limit": limit,
                "offset": offset,
                "returned": 0,
                "next_offset": None,
                "complete": True,
                "truncated": False,
            },
            "data": [],
        }

    request_limit = min(limit, available)
    effective_offset = max(total - offset - request_limit, 0)
    response = await collector_get_page(
        endpoint,
        params=_service_action_params(
            filters=filters,
            props=props,
            limit=request_limit,
            offset=effective_offset,
        ),
    )
    data = response.get("data", [])
    returned = len(data)
    complete = offset + returned >= total
    return {
        "pagination": {
            "limit": limit,
            "offset": offset,
            "returned": returned,
            "next_offset": None if complete else offset + returned,
            "complete": complete,
            "truncated": False,
        },
        "data": data,
    }


def _service_action_props(
    include_status_log: bool,
    include_status_log_preview: bool,
) -> str:
    props = SERVICE_ACTIONS_PROPS.split(",")
    if include_status_log or include_status_log_preview:
        props.append(SERVICE_ACTIONS_LOG_PROP)
    return ",".join(props)


def _service_action_filters(
    raw_filters: dict[str, str] | str | None = None,
    **criteria: str | None,
) -> list[tuple[str, str]]:
    filters: list[tuple[str, str]] = []
    filters.extend(_parse_service_filters(raw_filters))
    for field, value in criteria.items():
        if value is None:
            continue
        value = value.strip()
        if value:
            filters.append((field, value))
    return filters


def _service_unacknowledged_error_filters(
    raw_filters: dict[str, str] | str | None = None,
    **criteria: str | None,
) -> list[tuple[str, str]]:
    filters = _service_action_filters(raw_filters, **criteria)
    for field, _ in filters:
        normalized = field.rsplit(".", 1)[-1]
        if normalized in {"status", "ack"}:
            raise ValueError(
                "status and ack filters are implicit for "
                "actions_unacknowledged_errors"
            )
    return filters


def _service_action_params(
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


def _service_action_rows(
    rows: list[dict[str, Any]],
    include_status_log: bool,
    include_status_log_preview: bool,
    status_log_max_chars: int,
    latest_first: bool,
) -> list[dict[str, Any]]:
    shaped: list[dict[str, Any]] = []
    source_rows = reversed(rows) if latest_first else rows
    for row in source_rows:
        action = dict(row)
        status_log = action.get(SERVICE_ACTIONS_LOG_PROP)
        if status_log is not None and include_status_log_preview:
            action["status_log_preview"] = _truncate_text(
                str(status_log),
                status_log_max_chars,
            )
        if not include_status_log:
            action.pop(SERVICE_ACTIONS_LOG_PROP, None)
        shaped.append(action)
    return shaped

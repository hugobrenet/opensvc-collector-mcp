from typing import Any

from opensvc_collector_mcp.client import collector_get


DEFAULT_INVENTORY_STATS_FIELDS = (
    "status",
    "asset_env",
    "node_env",
    "loc_city",
    "loc_country",
    "app",
    "os_name",
)


async def get_nodes_inventory_stats(
    fields: str | None = None,
    page_size: int = 1000,
    max_nodes: int = 200000,
) -> dict[str, Any]:
    selected_fields = _parse_stats_fields(fields)
    page_size = max(1, min(page_size, 5000))
    max_nodes = max(1, min(max_nodes, 500000))
    counters: dict[str, dict[str, int]] = {field: {} for field in selected_fields}
    scanned = 0
    offset = 0
    total: int | None = None

    while scanned < max_nodes:
        response = await collector_get(
            "/nodes",
            params={
                "props": ",".join(selected_fields),
                "limit": min(page_size, max_nodes - scanned),
                "offset": offset,
            },
        )
        meta = response.get("meta", {})
        data = response.get("data", [])
        if total is None:
            total = meta.get("total")

        for node in data:
            for field in selected_fields:
                value = _stats_value(node.get(field))
                counters[field][value] = counters[field].get(value, 0) + 1

        count = len(data)
        scanned += count
        offset += count
        if count == 0 or count < page_size:
            break

    complete = total is None or scanned >= total
    return {
        "meta": {
            "total": total,
            "scanned": scanned,
            "complete": complete,
            "max_nodes": max_nodes,
            "fields": selected_fields,
        },
        "stats": {
            f"count_by_{field}": _sort_stats(counter)
            for field, counter in counters.items()
        },
    }


def _parse_stats_fields(fields: str | None) -> list[str]:
    if not fields:
        return list(DEFAULT_INVENTORY_STATS_FIELDS)
    selected = []
    for field in fields.split(","):
        field = field.strip()
        if field and field not in selected:
            selected.append(field)
    if not selected:
        raise ValueError("fields must contain at least one node property")
    return selected


def _stats_value(value: Any) -> str:
    if value is None or value == "":
        return "<empty>"
    return str(value)


def _sort_stats(counter: dict[str, int]) -> dict[str, int]:
    return dict(
        sorted(
            counter.items(),
            key=lambda item: (-item[1], item[0]),
        )
    )

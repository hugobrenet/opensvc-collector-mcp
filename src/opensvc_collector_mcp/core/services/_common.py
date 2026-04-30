from typing import Any


def _ensure_props_include(props: str, required_prop: str) -> str:
    parts = [part.strip() for part in props.split(",") if part.strip()]
    if not parts:
        return required_prop
    normalized = {part.rsplit(":", 1)[-1].rsplit(".", 1)[-1] for part in parts}
    if required_prop not in normalized:
        parts.append(required_prop)
    return ",".join(parts)


def _unresolved_node_ids(
    rows: list[dict[str, Any]],
    nodenames_by_node_id: dict[str, str],
) -> list[str]:
    return sorted(
        {
            node_id
            for row in rows
            if (node_id := str(row.get("node_id") or "").strip())
            and node_id not in nodenames_by_node_id
        }
    )


def _truncate_text(value: str, max_chars: int) -> str:
    if max_chars <= 0:
        return ""
    if len(value) <= max_chars:
        return value
    return f"{value[:max_chars]}..."


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_service_filters(raw_filters: dict[str, str] | str | None) -> list[tuple[str, str]]:
    if not raw_filters:
        return []
    if isinstance(raw_filters, dict):
        return [
            (field.strip(), value.strip())
            for field, value in raw_filters.items()
            if field.strip() and value.strip()
        ]

    filters: list[tuple[str, str]] = []
    for item in raw_filters.split(","):
        item = item.strip()
        if not item:
            continue
        if "=" not in item:
            raise ValueError("filters must use the format 'prop=value,prop=value'")
        field, value = item.split("=", 1)
        field = field.strip()
        value = value.strip()
        if not field or not value:
            raise ValueError("filters must not contain empty props or values")
        filters.append((field, value))
    return filters

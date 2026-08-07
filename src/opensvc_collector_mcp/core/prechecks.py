from collections.abc import Mapping
from typing import Any


def clean_value(value: Any) -> str:
    """Return a stripped string value for selector checks."""
    return str(value).strip() if value is not None else ""


def clean_selectors(selectors: Mapping[str, Any]) -> dict[str, str]:
    return {name: clean_value(value) for name, value in selectors.items()}


def require_exactly_one_selector(
    operation: str,
    selectors: Mapping[str, Any],
    *,
    selector_kind: str | None = None,
) -> dict[str, str]:
    cleaned = clean_selectors(selectors)
    selected = [name for name, value in cleaned.items() if value]
    if len(selected) != 1:
        label = f" {selector_kind}" if selector_kind else ""
        names = " or ".join(cleaned)
        raise ValueError(
            f"{operation} requires exactly one{label} selector: {names}"
        )
    return cleaned


def require_at_least_one_selector(
    operation: str,
    selectors: Mapping[str, Any],
    *,
    selector_kind: str | None = None,
    message: str | None = None,
) -> dict[str, str]:
    cleaned = clean_selectors(selectors)
    if not any(cleaned.values()):
        if message:
            raise ValueError(message)
        label = f" {selector_kind}" if selector_kind else ""
        names = " or ".join(cleaned)
        raise ValueError(f"{operation} requires at least one{label} selector: {names}")
    return cleaned


def require_single_row(
    response: Mapping[str, Any],
    *,
    not_found_message: str,
    multiple_message: str,
    invalid_message: str,
    exact_match_field: str | None = None,
    exact_match_value: Any = None,
) -> dict[str, Any]:
    rows = response.get("data", [])
    if not isinstance(rows, list) or not rows:
        raise ValueError(not_found_message)

    if exact_match_field is not None:
        expected = clean_value(exact_match_value)
        rows = [
            row
            for row in rows
            if isinstance(row, dict)
            and clean_value(row.get(exact_match_field)) == expected
        ]

    if len(rows) != 1:
        raise ValueError(multiple_message)

    row = rows[0]
    if not isinstance(row, dict):
        raise ValueError(invalid_message)
    return row


def require_identity(
    row: Mapping[str, Any],
    *,
    operation: str,
    target: str,
    id_field: str,
    name_field: str,
) -> tuple[str, str]:
    resolved_id = clean_value(row.get(id_field))
    resolved_name = clean_value(row.get(name_field))
    if not resolved_id:
        raise ValueError(f"{operation} resolved {target} has no {id_field}")
    if not resolved_name:
        raise ValueError(f"{operation} resolved {target} has no {name_field}")
    return resolved_id, resolved_name


def require_match(expected: Any, resolved: Any, *, message: str) -> None:
    expected_value = clean_value(expected)
    if expected_value and clean_value(resolved) != expected_value:
        raise ValueError(message)

from urllib.parse import quote


def require_selector(value: str, field: str) -> str:
    selector = value.strip()
    if not selector:
        raise ValueError(f"{field} must not be empty")
    return selector


def quote_selector(selector: str) -> str:
    return quote(selector, safe="")

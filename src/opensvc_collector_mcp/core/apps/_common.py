from urllib.parse import quote


def require_app_selector(app: str) -> str:
    selector = app.strip()
    if not selector:
        raise ValueError("app must not be empty")
    return selector


def quote_app_selector(selector: str) -> str:
    return quote(selector, safe="")

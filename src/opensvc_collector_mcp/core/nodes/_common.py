from typing import Any


def _first_node_row(response: dict[str, Any], nodename: str) -> dict[str, Any]:
    data = response.get("data", [])
    if data:
        return data[0]
    return {"nodename": nodename.strip()}


def _empty_to_none(value: Any) -> Any:
    if value == "":
        return None
    return value

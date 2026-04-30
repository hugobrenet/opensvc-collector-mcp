from typing import Any

from ._common import _first_node_row
from .inventory import get_node


async def get_node_organization(nodename: str) -> dict[str, Any]:
    response = await get_node(nodename)
    node = _first_node_row(response, nodename)
    raw = {
        "team_responsible": node.get("team_responsible"),
        "team_integ": node.get("team_integ"),
        "team_support": node.get("team_support"),
        "app": node.get("app"),
    }
    return {
        "nodename": nodename.strip(),
        "organization": {
            "responsible": node.get("team_responsible"),
            "integration": node.get("team_integ"),
            "support": node.get("team_support"),
            "app": node.get("app"),
        },
        "raw": raw,
    }

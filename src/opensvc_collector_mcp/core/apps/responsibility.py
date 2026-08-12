from typing import Any

from opensvc_collector_mcp.client import collector_get

from ._common import quote_app_selector, require_app_selector


async def am_i_responsible_for_app(app: str) -> dict[str, Any]:
    selector = require_app_selector(app)
    response = await collector_get(
        f"/apps/{quote_app_selector(selector)}/am_i_responsible"
    )
    return {
        "app": selector,
        "responsible": bool(response.get("data")),
        "meta": {
            "source": "apps/<id>/am_i_responsible",
            "selector": selector,
        },
    }

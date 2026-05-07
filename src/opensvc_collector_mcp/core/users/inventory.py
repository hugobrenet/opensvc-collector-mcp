from typing import Any

from opensvc_collector_mcp.client import collector_get


async def list_user_props() -> dict[str, Any]:
    response = await collector_get("/users", params={"props": "id", "limit": 1})
    available_props = response.get("meta", {}).get("available_props", [])
    user_props = [
        prop.removeprefix("auth_user.")
        for prop in available_props
        if isinstance(prop, str)
    ]

    return {
        "count": len(available_props),
        "available_props": available_props,
        "user_props": user_props,
    }

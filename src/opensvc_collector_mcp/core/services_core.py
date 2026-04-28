from typing import Any

from opensvc_collector_mcp.client import collector_get, collector_get_all


DEFAULT_LIST_SERVICE_PROPS = (
    "svcname,svc_app,svc_env,svc_status,svc_availstatus,svc_topology,"
    "svc_nodes,svc_drpnodes,svc_frozen,svc_ha,svc_created,updated"
)


async def list_services(props: str | None = None) -> dict[str, Any]:
    selected_props = props or DEFAULT_LIST_SERVICE_PROPS
    return await collector_get_all(
        "/services",
        params={"props": selected_props},
        strategy="paged",
    )


async def list_service_props() -> dict[str, Any]:
    response = await collector_get("/services", params={"props": "svcname"})
    available_props = response.get("meta", {}).get("available_props", [])
    service_props = [
        prop.removeprefix("services.")
        for prop in available_props
        if isinstance(prop, str)
    ]

    return {
        "count": len(available_props),
        "available_props": available_props,
        "service_props": service_props,
    }

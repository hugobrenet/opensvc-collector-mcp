from typing import Any

from ._common import _first_node_row
from .inventory import get_node


async def get_node_os(nodename: str) -> dict[str, Any]:
    response = await get_node(nodename)
    node = _first_node_row(response, nodename)
    raw = {
        "os_name": node.get("os_name"),
        "os_vendor": node.get("os_vendor"),
        "os_release": node.get("os_release"),
        "os_kernel": node.get("os_kernel"),
        "os_arch": node.get("os_arch"),
        "os_concat": node.get("os_concat"),
        "version": node.get("version"),
        "sp_version": node.get("sp_version"),
        "tz": node.get("tz"),
        "last_boot": node.get("last_boot"),
    }
    return {
        "nodename": nodename.strip(),
        "os": {
            "name": node.get("os_name"),
            "vendor": node.get("os_vendor"),
            "release": node.get("os_release"),
            "kernel": node.get("os_kernel"),
            "arch": node.get("os_arch"),
            "concat": node.get("os_concat"),
        },
        "runtime": {
            "version": node.get("version"),
            "service_pack": node.get("sp_version"),
            "timezone": node.get("tz"),
            "last_boot": node.get("last_boot"),
        },
        "raw": raw,
    }

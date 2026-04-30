from typing import Any

from ._common import _first_node_row
from .inventory import get_node


async def get_node_hardware(nodename: str) -> dict[str, Any]:
    response = await get_node(nodename)
    node = _first_node_row(response, nodename)
    raw = {
        "type": node.get("type"),
        "manufacturer": node.get("manufacturer"),
        "model": node.get("model"),
        "serial": node.get("serial"),
        "bios_version": node.get("bios_version"),
        "cpu_model": node.get("cpu_model"),
        "cpu_vendor": node.get("cpu_vendor"),
        "cpu_cores": node.get("cpu_cores"),
        "cpu_threads": node.get("cpu_threads"),
        "cpu_dies": node.get("cpu_dies"),
        "cpu_freq": node.get("cpu_freq"),
        "mem_bytes": node.get("mem_bytes"),
        "mem_banks": node.get("mem_banks"),
        "mem_slots": node.get("mem_slots"),
        "power_supply_nb": node.get("power_supply_nb"),
        "power_cabinet1": node.get("power_cabinet1"),
        "power_cabinet2": node.get("power_cabinet2"),
        "power_breaker1": node.get("power_breaker1"),
        "power_breaker2": node.get("power_breaker2"),
        "power_protect": node.get("power_protect"),
        "power_protect_breaker": node.get("power_protect_breaker"),
        "enclosure": node.get("enclosure"),
        "enclosureslot": node.get("enclosureslot"),
    }
    return {
        "nodename": nodename.strip(),
        "hardware": {
            "type": node.get("type"),
            "manufacturer": node.get("manufacturer"),
            "model": node.get("model"),
            "serial": node.get("serial"),
            "bios_version": node.get("bios_version"),
        },
        "cpu": {
            "model": node.get("cpu_model"),
            "vendor": node.get("cpu_vendor"),
            "cores": node.get("cpu_cores"),
            "threads": node.get("cpu_threads"),
            "dies": node.get("cpu_dies"),
            "frequency": node.get("cpu_freq"),
        },
        "memory": {
            "bytes": node.get("mem_bytes"),
            "banks": node.get("mem_banks"),
            "slots": node.get("mem_slots"),
        },
        "power": {
            "supply_count": node.get("power_supply_nb"),
            "cabinet1": node.get("power_cabinet1"),
            "cabinet2": node.get("power_cabinet2"),
            "breaker1": node.get("power_breaker1"),
            "breaker2": node.get("power_breaker2"),
            "protect": node.get("power_protect"),
            "protect_breaker": node.get("power_protect_breaker"),
        },
        "placement": {
            "enclosure": node.get("enclosure"),
            "enclosure_slot": node.get("enclosureslot"),
        },
        "raw": raw,
    }

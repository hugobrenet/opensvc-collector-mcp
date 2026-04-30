from typing import Any

from ._common import _first_node_row
from .inventory import get_node


async def get_node_location(nodename: str) -> dict[str, Any]:
    response = await get_node(nodename)
    node = _first_node_row(response, nodename)
    raw = {
        "loc_country": node.get("loc_country"),
        "loc_city": node.get("loc_city"),
        "loc_building": node.get("loc_building"),
        "loc_room": node.get("loc_room"),
        "loc_floor": node.get("loc_floor"),
        "loc_rack": node.get("loc_rack"),
        "enclosure": node.get("enclosure"),
        "enclosureslot": node.get("enclosureslot"),
        "loc_addr": node.get("loc_addr"),
        "loc_zip": node.get("loc_zip"),
    }
    return {
        "nodename": nodename.strip(),
        "location": {
            "country": node.get("loc_country"),
            "city": node.get("loc_city"),
            "building": node.get("loc_building"),
            "room": node.get("loc_room"),
            "floor": node.get("loc_floor"),
            "rack": node.get("loc_rack"),
            "enclosure": node.get("enclosure"),
            "enclosure_slot": node.get("enclosureslot"),
            "address": node.get("loc_addr"),
            "zip": node.get("loc_zip"),
        },
        "raw": raw,
    }

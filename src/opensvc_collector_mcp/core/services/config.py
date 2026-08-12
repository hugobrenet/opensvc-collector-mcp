from configparser import ConfigParser, Error as ConfigParserError
from typing import Any
from urllib.parse import quote

from opensvc_collector_mcp.client import collector_get

from ._common import _truncate_text


SERVICE_CONFIG_PROPS = "svcname,svc_config,svc_config_updated,updated"


async def get_service_config(
    svcname: str,
    include_raw_config: bool = True,
    include_sections: bool = True,
    raw_config_max_chars: int = 20000,
) -> dict[str, Any]:
    svcname = svcname.strip()
    if not svcname:
        raise ValueError("svcname must not be empty")

    raw_config_max_chars = max(0, min(raw_config_max_chars, 100000))
    response = await collector_get(
        f"/services/{quote(svcname, safe='')}",
        params={"props": SERVICE_CONFIG_PROPS},
    )
    rows = response.get("data", [])
    row = rows[0] if rows else {}
    raw_config = row.get("svc_config")
    config_text = raw_config if isinstance(raw_config, str) else ""
    config = (
        _truncate_text(config_text, raw_config_max_chars)
        if include_raw_config
        else None
    )
    sections = _parse_service_config_sections(config_text) if include_sections else []
    meta = dict(response.get("meta", {}))
    meta.update(
        {
            "source": "service_config",
            "filter": {"svcname": svcname},
            "included_props": SERVICE_CONFIG_PROPS.split(","),
            "config_present": bool(config_text),
            "config_length": len(config_text),
            "config_line_count": len(config_text.splitlines()) if config_text else 0,
            "section_count": len(sections),
            "include_raw_config": include_raw_config,
            "include_sections": include_sections,
            "raw_config_max_chars": raw_config_max_chars,
            "raw_config_truncated": bool(
                include_raw_config and len(config_text) > raw_config_max_chars
            ),
        }
    )
    return {
        "svcname": svcname,
        "meta": meta,
        "config_updated": row.get("svc_config_updated"),
        "updated": row.get("updated"),
        "config": config,
        "sections": sections,
    }


def _parse_service_config_sections(config_text: str) -> list[dict[str, Any]]:
    if not config_text.strip():
        return []

    parser = ConfigParser(interpolation=None, strict=False)
    parser.optionxform = str
    try:
        parser.read_string(config_text)
    except ConfigParserError:
        return []

    sections: list[dict[str, Any]] = []
    if parser.defaults():
        sections.append({"name": "DEFAULT", "options": dict(parser.defaults())})

    for section_name in parser.sections():
        section = parser[section_name]
        options = {
            key: value for key, value in section.items() if key not in parser.defaults()
        }
        sections.append({"name": section_name, "options": options})
    return sections

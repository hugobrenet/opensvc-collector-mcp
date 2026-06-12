"""Tag-domain business logic."""

from .inventory import (
    count_tag_nodes,
    count_tag_services,
    count_tags,
    create_tag,
    get_tag,
    get_tag_nodes,
    get_tag_services,
    list_tag_props,
    list_tags,
)

__all__ = [
    "count_tag_nodes",
    "count_tag_services",
    "count_tags",
    "create_tag",
    "get_tag",
    "get_tag_nodes",
    "get_tag_services",
    "list_tag_props",
    "list_tags",
]

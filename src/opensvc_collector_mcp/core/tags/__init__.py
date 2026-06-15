"""Tag-domain business logic."""

from .inventory import (
    attach_tag_to_node,
    count_tag_nodes,
    count_tag_services,
    count_tags,
    create_tag,
    delete_tag,
    get_tag,
    get_tag_nodes,
    get_tag_services,
    list_tag_props,
    list_tags,
)

__all__ = [
    "attach_tag_to_node",
    "count_tag_nodes",
    "count_tag_services",
    "count_tags",
    "create_tag",
    "delete_tag",
    "get_tag",
    "get_tag_nodes",
    "get_tag_services",
    "list_tag_props",
    "list_tags",
]

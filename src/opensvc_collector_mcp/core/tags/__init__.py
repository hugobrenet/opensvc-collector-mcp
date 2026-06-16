"""Tag-domain business logic."""

from .inventory import (
    attach_tag_to_node,
    attach_tag_to_service,
    count_tag_nodes,
    count_tag_services,
    count_tags,
    create_tag,
    delete_tag,
    detach_tag_from_node,
    get_tag,
    get_tag_nodes,
    get_tag_services,
    list_tag_props,
    list_tags,
)

__all__ = [
    "attach_tag_to_node",
    "attach_tag_to_service",
    "count_tag_nodes",
    "count_tag_services",
    "count_tags",
    "create_tag",
    "delete_tag",
    "detach_tag_from_node",
    "get_tag",
    "get_tag_nodes",
    "get_tag_services",
    "list_tag_props",
    "list_tags",
]

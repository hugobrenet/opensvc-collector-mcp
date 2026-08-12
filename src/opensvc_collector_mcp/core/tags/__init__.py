"""Tag-domain business logic."""

from .inventory import (
    count_tags,
    get_tag,
    list_tag_props,
    list_tags,
)

from .mutations import create_tag, delete_tag

from .node_relations import (
    attach_tag_to_node,
    count_tag_nodes,
    detach_tag_from_node,
    get_tag_nodes,
)

from .service_relations import (
    attach_tag_to_service,
    count_tag_services,
    detach_tag_from_service,
    get_tag_services,
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
    "detach_tag_from_service",
    "get_tag",
    "get_tag_nodes",
    "get_tag_services",
    "list_tag_props",
    "list_tags",
]

"""Pydantic contracts for tag tools."""

from ._common import (
    TagSelector,
)

from .inventory import (
    AttachTagToNodeRequest,
    AttachTagToNodeResponse,
    CountTagServicesRequest,
    CountTagsRequest,
    CountTagsResponse,
    CreateTagRequest,
    CreateTagResponse,
    DeleteTagRequest,
    DeleteTagResponse,
    ListTagsRequest,
    TagFilterRequest,
    TagIdentityRequest,
    TagNodesRequest,
    TagNodesResponse,
    TagServicesRequest,
    TagServicesResponse,
    TagPropsResponse,
    TagRow,
    TagRelationCountResponse,
    TagSelectorRequest,
    TagRowsResponse,
)

__all__ = [
    "AttachTagToNodeRequest",
    "AttachTagToNodeResponse",
    "CountTagServicesRequest",
    "CountTagsRequest",
    "CountTagsResponse",
    "CreateTagRequest",
    "CreateTagResponse",
    "DeleteTagRequest",
    "DeleteTagResponse",
    "ListTagsRequest",
    "TagFilterRequest",
    "TagIdentityRequest",
    "TagNodesRequest",
    "TagNodesResponse",
    "TagServicesRequest",
    "TagServicesResponse",
    "TagPropsResponse",
    "TagRow",
    "TagRelationCountResponse",
    "TagSelector",
    "TagSelectorRequest",
    "TagRowsResponse",
]

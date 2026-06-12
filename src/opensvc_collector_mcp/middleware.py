"""Compatibility imports for auth middleware.

New code should import from opensvc_collector_mcp.auth.* directly.
"""

from opensvc_collector_mcp.auth.basic import CollectorBasicAuthMiddleware
from opensvc_collector_mcp.auth.middleware import (
    AI_REQUEST_ID_HEADER,
    CollectorReadToolAuthorizationMiddleware,
    ToolSchemaValidationErrorMiddleware,
)

__all__ = [
    "AI_REQUEST_ID_HEADER",
    "CollectorBasicAuthMiddleware",
    "CollectorReadToolAuthorizationMiddleware",
    "ToolSchemaValidationErrorMiddleware",
]

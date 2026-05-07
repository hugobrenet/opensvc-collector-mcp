"""User-domain business logic."""

from .inventory import (
    get_user,
    list_user_props,
    list_users,
    search_users_by_group,
    search_users_by_primary_group,
)

__all__ = [
    "get_user",
    "list_user_props",
    "list_users",
    "search_users_by_group",
    "search_users_by_primary_group",
]

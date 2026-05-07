"""User-domain business logic."""

from .inventory import (
    count_users,
    count_users_by_group,
    count_users_by_primary_group,
    get_user,
    list_user_props,
    list_users,
    search_users_by_group,
    search_users_by_primary_group,
)

__all__ = [
    "count_users",
    "count_users_by_group",
    "count_users_by_primary_group",
    "get_user",
    "list_user_props",
    "list_users",
    "search_users_by_group",
    "search_users_by_primary_group",
]

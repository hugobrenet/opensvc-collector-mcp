"""Array-domain business logic."""

from .inventory import (
    count_array_diskgroups,
    count_arrays,
    get_array,
    get_array_diskgroup,
    get_array_diskgroups,
    list_array_props,
    list_arrays,
)

__all__ = [
    "count_array_diskgroups",
    "count_arrays",
    "get_array",
    "get_array_diskgroup",
    "get_array_diskgroups",
    "list_array_props",
    "list_arrays",
]

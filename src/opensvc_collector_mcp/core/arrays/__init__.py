"""Array-domain business logic."""

from .diskgroups import (
    count_array_diskgroups,
    get_array_diskgroup,
    get_array_diskgroups,
    list_array_diskgroups,
)
from .inventory import (
    count_arrays,
    get_array,
    list_array_props,
    list_arrays,
)
from .quotas import get_array_diskgroup_quota, get_array_diskgroup_quotas
from .relations import get_array_proxies, get_array_targets

__all__ = [
    "count_array_diskgroups",
    "count_arrays",
    "get_array",
    "get_array_diskgroup",
    "get_array_diskgroup_quota",
    "get_array_diskgroup_quotas",
    "get_array_diskgroups",
    "get_array_proxies",
    "get_array_targets",
    "list_array_props",
    "list_array_diskgroups",
    "list_arrays",
]

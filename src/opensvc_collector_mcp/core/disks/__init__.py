"""Disk-domain business logic."""

from .inventory import (
    count_disks,
    get_disk,
    list_disk_props,
    list_disks,
)

__all__ = [
    "count_disks",
    "get_disk",
    "list_disk_props",
    "list_disks",
]

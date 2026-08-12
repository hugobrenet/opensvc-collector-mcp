"""Node-domain business logic."""

from .inventory import (
    list_nodes,
    list_node_props,
    count_nodes,
    get_node,
)

from .mutations import (
    create_node,
    update_node_properties,
    delete_node,
)

from .actions import (
    freeze_node,
    thaw_node,
    run_node_checks,
    collect_node_sysreport,
    push_node_asset,
    push_node_disks,
    push_node_packages,
    push_node_patches,
    push_node_stats,
    pull_node_config,
    push_node_config,
    update_node_compliance_modules,
    update_node_opensvc_agent,
    scan_node_scsi,
    reboot_node,
    shutdown_node,
    schedule_node_reboot,
    unschedule_node_reboot,
    rotate_node_root_password,
    wake_node_on_lan,
)

from .notifications import (
    snooze_node_notifications,
    unsnooze_node_notifications,
)

from .tags import (
    get_node_tags,
)

from .location import (
    get_node_location,
)

from .organization import (
    get_node_organization,
)

from .hardware import (
    get_node_hardware,
)

from .os import (
    get_node_os,
)

from .cluster import (
    get_node_cluster,
)

from .network import (
    get_node_network,
)

from .compliance import (
    get_node_compliance,
)

from .checks import (
    get_node_checks,
)

from .storage import (
    get_node_disks,
)

from .services import (
    get_node_services,
)

from .health import (
    get_node_health,
)

from .stats import (
    get_nodes_inventory_stats,
)

__all__ = [
    'count_nodes',
    'create_node',
    'delete_node',
    'freeze_node',
    'thaw_node',
    'run_node_checks',
    'collect_node_sysreport',
    'push_node_asset',
    'push_node_disks',
    'push_node_packages',
    'push_node_patches',
    'push_node_stats',
    'pull_node_config',
    'push_node_config',
    'update_node_compliance_modules',
    'update_node_opensvc_agent',
    'scan_node_scsi',
    'reboot_node',
    'shutdown_node',
    'schedule_node_reboot',
    'unschedule_node_reboot',
    'rotate_node_root_password',
    'wake_node_on_lan',
    'get_node',
    'get_node_checks',
    'get_node_cluster',
    'get_node_compliance',
    'get_node_disks',
    'get_node_hardware',
    'get_node_health',
    'get_node_location',
    'get_node_network',
    'get_node_organization',
    'get_node_os',
    'get_node_services',
    'get_node_tags',
    'get_nodes_inventory_stats',
    'list_node_props',
    'snooze_node_notifications',
    'unsnooze_node_notifications',
    'update_node_properties',
    'list_nodes',
]

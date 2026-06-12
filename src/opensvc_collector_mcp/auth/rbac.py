from dataclasses import dataclass


READ_AUTHORIZATION_TAG = "read"
AUTHORIZATION_TAG_PREFIXES = (
    "write:",
    "delete:",
    "exec:",
    "operate:",
    "push:",
    "upload:",
)

DEFAULT_TOOL_AUTHORIZATION_POLICY: dict[str, set[str]] = {
    "read": {"Everybody", "Manager"},
    "write:nodes": {"NodeManager", "Manager"},
    "delete:nodes": {"NodeManager", "Manager"},
    "exec:nodes": {"NodeExec", "Manager"},
    "write:apps": {"AppManager", "Manager"},
    "write:users": {"UserManager", "Manager"},
    "write:users:self": {"SelfManager", "UserManager", "Manager"},
    "write:users:primary_group:self": {"SelfManager", "UserManager", "Manager"},
    "write:groups": {"GroupManager", "Manager"},
    "write:privilege_groups": {"Manager"},
    "write:compliance": {"CompManager", "Manager"},
    "exec:compliance": {"CompExec", "Manager"},
    "write:checks": {"CheckManager", "Manager"},
    "exec:checks": {"CheckExec", "Manager"},
    "write:context_checks": {"ContextCheckManager", "Manager"},
    "write:storage": {"StorageManager", "Manager"},
    "write:networks": {"NetworkManager", "Manager"},
    "write:tags": {"TagManager", "Manager"},
    "delete:tags": {"TagManager", "Manager"},
    "write:dns": {"DnsManager", "Manager"},
    "operate:dns": {"DnsOperator", "Manager"},
    "write:reports": {"ReportsManager", "Manager"},
    "write:charts": {"ChartsManager", "Manager"},
    "write:forms": {"FormsManager", "Manager"},
    "write:provisioning_templates": {"ProvisioningManager", "Manager"},
    "write:docker_registries": {"DockerRegistriesManager", "Manager"},
    "push:docker_registries": {"DockerRegistriesPusher", "Manager"},
    "write:alerts": {"AlertsManager", "Manager"},
    "write:obsolescence": {"ObsManager", "Manager"},
    "upload:safe": {"SafeUploader", "Manager"},
    "write:scheduler": {"Manager"},
    "write:sysreport": {"Manager"},
    "write:replication": {"ReplicationManager", "Manager"},
    "write:quotas": {"QuotaManager", "Manager"},
}


@dataclass(frozen=True)
class ToolAuthorizationRequirement:
    tag: str
    groups: set[str]


@dataclass(frozen=True)
class ToolAuthorizationDecision:
    allowed: bool
    reason: str | None
    requirement: ToolAuthorizationRequirement | None
    tool_tags: set[str]
    authorization_tags: set[str]
    user_groups: set[str] | None


def is_authorization_tag(tag: str) -> bool:
    return tag == READ_AUTHORIZATION_TAG or tag.startswith(AUTHORIZATION_TAG_PREFIXES)


def authorization_tags(tool_tags: set[str]) -> set[str]:
    return {tag for tag in tool_tags if is_authorization_tag(tag)}


def resolve_tool_requirement(
    tool_tags: set[str],
    *,
    authorization_policy: dict[str, set[str]] | None = None,
) -> tuple[ToolAuthorizationRequirement | None, str | None, set[str]]:
    policy = authorization_policy or DEFAULT_TOOL_AUTHORIZATION_POLICY
    auth_tags = authorization_tags(tool_tags)

    if not auth_tags:
        return None, "missing_authorization_tag", auth_tags

    unknown_tags = auth_tags - set(policy)
    if unknown_tags:
        return None, "unknown_authorization_tag", auth_tags

    if len(auth_tags) != 1:
        return None, "mixed_authorization_tags", auth_tags

    tag = next(iter(auth_tags))
    return ToolAuthorizationRequirement(tag=tag, groups=policy[tag]), None, auth_tags


def authorize_tool(
    *,
    tool_tags: set[str],
    user_groups: set[str] | None,
    authorization_policy: dict[str, set[str]] | None = None,
) -> ToolAuthorizationDecision:
    requirement, reason, auth_tags = resolve_tool_requirement(
        tool_tags,
        authorization_policy=authorization_policy,
    )
    if requirement is None:
        return ToolAuthorizationDecision(
            allowed=False,
            reason=reason,
            requirement=None,
            tool_tags=tool_tags,
            authorization_tags=auth_tags,
            user_groups=user_groups,
        )

    if user_groups is None or not requirement.groups & user_groups:
        return ToolAuthorizationDecision(
            allowed=False,
            reason="missing_required_group",
            requirement=requirement,
            tool_tags=tool_tags,
            authorization_tags=auth_tags,
            user_groups=user_groups,
        )

    return ToolAuthorizationDecision(
        allowed=True,
        reason=None,
        requirement=requirement,
        tool_tags=tool_tags,
        authorization_tags=auth_tags,
        user_groups=user_groups,
    )

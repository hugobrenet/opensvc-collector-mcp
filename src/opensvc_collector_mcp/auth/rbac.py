from dataclasses import dataclass


DEFAULT_READ_TAG = "read"
DEFAULT_READ_GROUPS = {"Everybody", "Manager"}


@dataclass(frozen=True)
class ToolAuthorizationRequirement:
    tag: str
    groups: set[str]


@dataclass(frozen=True)
class ToolAuthorizationDecision:
    allowed: bool
    reason: str | None
    requirement: ToolAuthorizationRequirement
    tool_tags: set[str]
    user_groups: set[str] | None


def read_tool_requirement(
    *,
    read_tag: str = DEFAULT_READ_TAG,
    read_groups: set[str] | None = None,
) -> ToolAuthorizationRequirement:
    return ToolAuthorizationRequirement(
        tag=read_tag,
        groups=read_groups or DEFAULT_READ_GROUPS,
    )


def authorize_read_tool(
    *,
    tool_tags: set[str],
    user_groups: set[str] | None,
    read_tag: str = DEFAULT_READ_TAG,
    read_groups: set[str] | None = None,
) -> ToolAuthorizationDecision:
    requirement = read_tool_requirement(
        read_tag=read_tag,
        read_groups=read_groups,
    )
    if requirement.tag not in tool_tags:
        return ToolAuthorizationDecision(
            allowed=False,
            reason="missing_required_tag",
            requirement=requirement,
            tool_tags=tool_tags,
            user_groups=user_groups,
        )

    if user_groups is None or not requirement.groups & user_groups:
        return ToolAuthorizationDecision(
            allowed=False,
            reason="missing_required_group",
            requirement=requirement,
            tool_tags=tool_tags,
            user_groups=user_groups,
        )

    return ToolAuthorizationDecision(
        allowed=True,
        reason=None,
        requirement=requirement,
        tool_tags=tool_tags,
        user_groups=user_groups,
    )

from opensvc_collector_mcp.auth.rbac import (
    DEFAULT_TOOL_AUTHORIZATION_POLICY,
    authorization_tags,
    authorize_tool,
    resolve_tool_requirement,
)


def test_authorization_tags_extracts_only_authorization_tags():
    assert authorization_tags({"nodes", "inventory", "read"}) == {"read"}
    assert authorization_tags({"nodes", "write:nodes"}) == {"write:nodes"}
    assert authorization_tags({"nodes", "update", "write:nodes"}) == {"write:nodes"}
    assert authorization_tags({"tags", "create", "write:tags"}) == {"write:tags"}
    assert authorization_tags({"tags", "delete", "delete:tags"}) == {"delete:tags"}
    assert authorization_tags({"nodes", "delete", "delete:nodes"}) == {"delete:nodes"}
    assert authorization_tags({"nodes", "count"}) == set()


def test_resolve_tool_requirement_returns_policy_groups():
    requirement, reason, auth_tags = resolve_tool_requirement({"nodes", "write:nodes"})

    assert reason is None
    assert auth_tags == {"write:nodes"}
    assert requirement is not None
    assert requirement.tag == "write:nodes"
    assert requirement.groups == {"NodeManager", "Manager"}


def test_authorize_tool_allows_read_with_everybody():
    decision = authorize_tool(
        tool_tags={"read", "nodes"},
        user_groups={"Everybody"},
    )

    assert decision.allowed is True
    assert decision.reason is None
    assert decision.requirement is not None
    assert decision.requirement.tag == "read"
    assert decision.requirement.groups == {"Everybody", "Manager"}
    assert decision.user_groups == {"Everybody"}


def test_authorize_tool_allows_write_nodes_with_node_manager():
    decision = authorize_tool(
        tool_tags={"write:nodes"},
        user_groups={"NodeManager"},
    )

    assert decision.allowed is True
    assert decision.reason is None
    assert decision.requirement is not None
    assert decision.requirement.tag == "write:nodes"
    assert decision.requirement.groups == {"NodeManager", "Manager"}


def test_authorize_tool_allows_write_nodes_with_manager_override():
    decision = authorize_tool(
        tool_tags={"write:nodes"},
        user_groups={"Manager"},
    )

    assert decision.allowed is True
    assert decision.reason is None
    assert decision.requirement is not None
    assert decision.requirement.tag == "write:nodes"


def test_authorize_tool_denies_missing_authorization_tag():
    decision = authorize_tool(
        tool_tags={"nodes", "inventory"},
        user_groups={"Manager"},
    )

    assert decision.allowed is False
    assert decision.reason == "missing_authorization_tag"
    assert decision.requirement is None
    assert decision.authorization_tags == set()


def test_authorize_tool_denies_unknown_authorization_tag():
    decision = authorize_tool(
        tool_tags={"write:unknown"},
        user_groups={"Manager"},
    )

    assert decision.allowed is False
    assert decision.reason == "unknown_authorization_tag"
    assert decision.requirement is None
    assert decision.authorization_tags == {"write:unknown"}


def test_authorize_tool_denies_mixed_authorization_tags():
    decision = authorize_tool(
        tool_tags={"read", "write:nodes"},
        user_groups={"Manager"},
    )

    assert decision.allowed is False
    assert decision.reason == "mixed_authorization_tags"
    assert decision.requirement is None
    assert decision.authorization_tags == {"read", "write:nodes"}


def test_authorize_tool_denies_missing_required_group():
    decision = authorize_tool(
        tool_tags={"write:nodes"},
        user_groups={"Everybody"},
    )

    assert decision.allowed is False
    assert decision.reason == "missing_required_group"
    assert decision.requirement is not None
    assert decision.requirement.tag == "write:nodes"
    assert decision.requirement.groups == {"NodeManager", "Manager"}
    assert decision.user_groups == {"Everybody"}


def test_authorize_tool_allows_delete_tags_with_tag_manager():
    decision = authorize_tool(
        tool_tags={"delete:tags", "tags"},
        user_groups={"TagManager"},
    )

    assert decision.allowed is True
    assert decision.reason is None
    assert decision.requirement is not None
    assert decision.requirement.tag == "delete:tags"
    assert decision.requirement.groups == {"TagManager", "Manager"}


def test_authorize_tool_allows_delete_nodes_with_node_manager():
    decision = authorize_tool(
        tool_tags={"delete:nodes", "nodes"},
        user_groups={"NodeManager"},
    )

    assert decision.allowed is True
    assert decision.reason is None
    assert decision.requirement is not None
    assert decision.requirement.tag == "delete:nodes"
    assert decision.requirement.groups == {"NodeManager", "Manager"}


def test_default_policy_contains_expected_write_groups():
    assert DEFAULT_TOOL_AUTHORIZATION_POLICY["write:users:self"] == {
        "SelfManager",
        "UserManager",
        "Manager",
    }
    assert DEFAULT_TOOL_AUTHORIZATION_POLICY["exec:compliance"] == {
        "CompExec",
        "Manager",
    }
    assert DEFAULT_TOOL_AUTHORIZATION_POLICY["delete:tags"] == {
        "TagManager",
        "Manager",
    }

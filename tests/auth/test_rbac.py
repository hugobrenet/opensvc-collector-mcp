from opensvc_collector_mcp.auth.rbac import authorize_read_tool


def test_authorize_read_tool_allows_required_group():
    decision = authorize_read_tool(
        tool_tags={"read", "nodes"},
        user_groups={"Everybody"},
    )

    assert decision.allowed is True
    assert decision.reason is None
    assert decision.requirement.tag == "read"
    assert decision.requirement.groups == {"Everybody", "Manager"}
    assert decision.user_groups == {"Everybody"}


def test_authorize_read_tool_denies_missing_read_tag():
    decision = authorize_read_tool(
        tool_tags={"write:nodes"},
        user_groups=None,
    )

    assert decision.allowed is False
    assert decision.reason == "missing_required_tag"
    assert decision.requirement.tag == "read"
    assert decision.user_groups is None


def test_authorize_read_tool_denies_missing_required_group():
    decision = authorize_read_tool(
        tool_tags={"read"},
        user_groups={"TeamA"},
    )

    assert decision.allowed is False
    assert decision.reason == "missing_required_group"
    assert decision.requirement.groups == {"Everybody", "Manager"}
    assert decision.user_groups == {"TeamA"}

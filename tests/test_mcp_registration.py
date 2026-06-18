import pytest

from opensvc_collector_mcp.server import build_mcp

EXPECTED_TOOL_NAMES = {
    "am_i_responsible_for_app",
    "attach_tag_to_node",
    "attach_tag_to_service",
    "count_app_nodes",
    "count_app_services",
    "count_apps",
    "count_array_diskgroups",
    "count_arrays",
    "count_disks",
    "count_nodes",
    "count_services",
    "count_tag_nodes",
    "count_tag_services",
    "count_tags",
    "count_users",
    "count_users_by_group",
    "count_users_by_primary_group",
    "create_node",
    "create_tag",
    "delete_node",
    "delete_tag",
    "detach_tag_from_node",
    "detach_tag_from_service",
    "freeze_node",
    "thaw_node",
    "run_node_checks",
    "collect_node_sysreport",
    "push_node_asset",
    "push_node_disks",
    "push_node_stats",
    "pull_node_config",
    "push_node_config",
    "get_app",
    "get_app_nodes",
    "get_app_publications",
    "get_app_quotas",
    "get_app_responsibles",
    "get_app_services",
    "get_array",
    "get_array_diskgroup",
    "get_array_diskgroup_quota",
    "get_array_diskgroup_quotas",
    "get_array_diskgroups",
    "get_array_proxies",
    "get_array_targets",
    "get_cluster_nodes",
    "get_compliance_logs",
    "get_compliance_moduleset",
    "get_compliance_moduleset_candidate_nodes",
    "get_compliance_moduleset_candidate_services",
    "get_compliance_moduleset_definition",
    "get_compliance_moduleset_modules",
    "get_compliance_moduleset_nodes",
    "get_compliance_moduleset_publications",
    "get_compliance_moduleset_responsibles",
    "get_compliance_moduleset_services",
    "get_compliance_moduleset_usage",
    "get_compliance_ruleset",
    "get_compliance_ruleset_candidate_nodes",
    "get_compliance_ruleset_candidate_services",
    "get_compliance_ruleset_publications",
    "get_compliance_ruleset_responsibles",
    "get_compliance_ruleset_usage",
    "get_compliance_ruleset_variable",
    "get_compliance_ruleset_variables",
    "get_compliance_run_detail",
    "get_compliance_status",
    "get_disk",
    "get_node",
    "get_node_checks",
    "get_node_cluster",
    "get_node_compliance",
    "get_node_disks",
    "get_node_hardware",
    "get_node_health",
    "get_node_location",
    "get_node_network",
    "get_node_organization",
    "get_node_os",
    "get_node_services",
    "get_node_tags",
    "get_nodes_inventory_stats",
    "get_service",
    "get_service_actions",
    "get_service_alerts",
    "get_service_checks",
    "get_service_compliance_logs",
    "get_service_compliance_status",
    "get_service_config",
    "get_service_disks",
    "get_service_hbas",
    "get_service_health",
    "get_service_instance_status_history",
    "get_service_instances",
    "get_service_nodes",
    "get_service_resource_status",
    "get_service_resources",
    "get_service_status_history",
    "get_service_tags",
    "get_service_targets",
    "get_service_unacknowledged_errors",
    "get_tag",
    "get_tag_nodes",
    "get_tag_services",
    "get_user",
    "list_app_props",
    "list_apps",
    "list_array_diskgroups",
    "list_array_props",
    "list_arrays",
    "list_compliance_modulesets",
    "list_compliance_rulesets",
    "list_disk_props",
    "list_disks",
    "list_node_props",
    "list_nodes",
    "list_service_props",
    "list_services",
    "list_tag_props",
    "list_tags",
    "list_user_props",
    "list_users",
    "search_frozen_services",
    "search_users_by_group",
    "search_users_by_primary_group",
    "snooze_node_notifications",
    "unsnooze_node_notifications",
    "update_node_properties",
}


async def test_all_expected_tools_are_registered_in_underlying_catalog():
    tools = await build_mcp()._list_tools()
    tool_names = {tool.name for tool in tools}

    assert tool_names == EXPECTED_TOOL_NAMES
    assert len(tool_names) == len(tools)


async def test_attach_tag_to_node_is_marked_as_non_destructive_write():
    tools = await build_mcp()._list_tools()
    tool = next(tool for tool in tools if tool.name == "attach_tag_to_node")

    assert tool.annotations.readOnlyHint is False
    assert tool.annotations.idempotentHint is False
    assert tool.annotations.destructiveHint is False


async def test_attach_tag_to_service_is_marked_as_non_destructive_write():
    tools = await build_mcp()._list_tools()
    tool = next(tool for tool in tools if tool.name == "attach_tag_to_service")

    assert tool.annotations.readOnlyHint is False
    assert tool.annotations.idempotentHint is False
    assert tool.annotations.destructiveHint is False


async def test_detach_tag_from_node_is_marked_as_destructive_write():
    tools = await build_mcp()._list_tools()
    tool = next(tool for tool in tools if tool.name == "detach_tag_from_node")

    assert tool.annotations.readOnlyHint is False
    assert tool.annotations.idempotentHint is False
    assert tool.annotations.destructiveHint is True


async def test_detach_tag_from_service_is_marked_as_destructive_write():
    tools = await build_mcp()._list_tools()
    tool = next(tool for tool in tools if tool.name == "detach_tag_from_service")

    assert tool.annotations.readOnlyHint is False
    assert tool.annotations.idempotentHint is False
    assert tool.annotations.destructiveHint is True


async def test_freeze_node_is_marked_as_destructive_exec():
    tools = await build_mcp()._list_tools()
    tool = next(tool for tool in tools if tool.name == "freeze_node")

    assert tool.annotations.readOnlyHint is False
    assert tool.annotations.idempotentHint is False
    assert tool.annotations.destructiveHint is True


async def test_thaw_node_is_marked_as_destructive_exec():
    tools = await build_mcp()._list_tools()
    tool = next(tool for tool in tools if tool.name == "thaw_node")

    assert tool.annotations.readOnlyHint is False
    assert tool.annotations.idempotentHint is False
    assert tool.annotations.destructiveHint is True


@pytest.mark.parametrize(
    "name",
    [
        "run_node_checks",
        "collect_node_sysreport",
        "push_node_asset",
        "push_node_disks",
        "push_node_stats",
        "pull_node_config",
        "push_node_config",
    ],
)
async def test_low_risk_node_exec_actions_are_marked_as_non_destructive_exec(name):
    tools = await build_mcp()._list_tools()
    tool = next(tool for tool in tools if tool.name == name)

    assert tool.annotations.readOnlyHint is False
    assert tool.annotations.idempotentHint is False
    assert tool.annotations.destructiveHint is False


async def test_create_node_is_marked_as_destructive_write():
    tools = await build_mcp()._list_tools()
    tool = next(tool for tool in tools if tool.name == "create_node")

    assert tool.annotations.readOnlyHint is False
    assert tool.annotations.idempotentHint is False
    assert tool.annotations.destructiveHint is True


async def test_create_node_schema_rejects_reserved_properties():
    tools = await build_mcp()._list_tools()
    tool = next(tool for tool in tools if tool.name == "create_node")

    request_schema = tool.parameters["$defs"]["CreateNodeRequest"]
    properties_schema = request_schema["properties"]["properties"]

    assert properties_schema["propertyNames"] == {
        "not": {"enum": ["node_id", "nodename"]}
    }


async def test_delete_node_is_marked_as_destructive_write():
    tools = await build_mcp()._list_tools()
    tool = next(tool for tool in tools if tool.name == "delete_node")

    assert tool.annotations.readOnlyHint is False
    assert tool.annotations.idempotentHint is False
    assert tool.annotations.destructiveHint is True


async def test_delete_node_schema_distinguishes_selector_from_confirmation():
    tools = await build_mcp()._list_tools()
    tool = next(tool for tool in tools if tool.name == "delete_node")

    assert "node_id-only" in tool.description
    assert "first call get_node" in tool.description
    assert "Do not ask for a delete confirmation before this resolution" in tool.description
    assert "Do not pass nodename as an execution selector" in tool.description

    request_schema = tool.parameters["$defs"]["DeleteNodeRequest"]
    properties = request_schema["properties"]
    node_id_description = properties["node_id"]["description"]
    confirm_nodename_description = properties["confirm_nodename"]["description"]
    confirmation_description = properties["confirmation"]["description"]
    example = request_schema["examples"][0]

    assert "Required execution selector" in node_id_description
    assert "Never pass nodename as node_id" in node_id_description
    assert "nodename" not in properties
    assert "not a second selector" in confirm_nodename_description
    assert "delete_node execution uses node_id only" in confirmation_description
    assert "node_id" in request_schema["required"]
    assert example["node_id"] == "NODE-ID"
    assert "nodename" not in example
    assert example["confirm_nodename"] == "lab-node-01"


@pytest.mark.parametrize(
    "name",
    [
        "freeze_node",
        "thaw_node",
        "run_node_checks",
        "collect_node_sysreport",
        "push_node_asset",
        "push_node_disks",
        "push_node_stats",
        "pull_node_config",
        "push_node_config",
        "update_node_properties",
        "snooze_node_notifications",
        "unsnooze_node_notifications",
    ],
)
async def test_existing_node_state_changing_tools_are_node_id_only(name):
    tools = await build_mcp()._list_tools()
    tool = next(tool for tool in tools if tool.name == name)

    assert "node_id-only" in tool.description
    assert "first call get_node" in tool.description
    assert "Do not pass nodename as an execution selector" in tool.description

    request_ref = tool.parameters["properties"]["request"]["$ref"]
    request_name = request_ref.removeprefix("#/$defs/")
    request_schema = tool.parameters["$defs"][request_name]
    properties = request_schema["properties"]

    assert "node_id" in request_schema["required"]
    assert "node_id" in properties
    assert "nodename" not in properties
    assert "confirm_node_id" in properties
    assert "confirm_nodename" in properties


@pytest.mark.parametrize(
    "name",
    [
        "delete_tag",
        "attach_tag_to_node",
        "attach_tag_to_service",
        "detach_tag_from_node",
        "detach_tag_from_service",
    ],
)
async def test_existing_tag_state_changing_tools_are_tag_id_only(name):
    tools = await build_mcp()._list_tools()
    tool = next(tool for tool in tools if tool.name == name)

    assert "tag_id-only" in tool.description
    assert "first call get_tag" in tool.description
    assert "Do not pass tag_name as an execution selector" in tool.description

    request_ref = tool.parameters["properties"]["request"]["$ref"]
    request_name = request_ref.removeprefix("#/$defs/")
    request_schema = tool.parameters["$defs"][request_name]
    properties = request_schema["properties"]

    assert "tag_id" in request_schema["required"]
    assert "tag_id" in properties
    assert "tag_name" not in properties
    assert "confirm_tag_id" in properties
    assert "confirm_tag_name" in properties


async def test_snooze_node_notifications_is_marked_as_non_destructive_write():
    tools = await build_mcp()._list_tools()
    tool = next(tool for tool in tools if tool.name == "snooze_node_notifications")

    assert tool.annotations.readOnlyHint is False
    assert tool.annotations.idempotentHint is False
    assert tool.annotations.destructiveHint is False


async def test_unsnooze_node_notifications_is_marked_as_non_destructive_write():
    tools = await build_mcp()._list_tools()
    tool = next(tool for tool in tools if tool.name == "unsnooze_node_notifications")

    assert tool.annotations.readOnlyHint is False
    assert tool.annotations.idempotentHint is False
    assert tool.annotations.destructiveHint is False


async def test_update_node_properties_is_marked_as_destructive_write():
    tools = await build_mcp()._list_tools()
    tool = next(tool for tool in tools if tool.name == "update_node_properties")

    assert tool.annotations.readOnlyHint is False
    assert tool.annotations.idempotentHint is False
    assert tool.annotations.destructiveHint is True


async def test_state_changing_tools_require_confirmation_phrase_in_schema():
    tools = await build_mcp()._list_tools()
    tools_by_name = {tool.name: tool for tool in tools}

    for name in {
        "attach_tag_to_node",
        "attach_tag_to_service",
        "create_tag",
        "delete_tag",
        "detach_tag_from_node",
        "detach_tag_from_service",
        "freeze_node",
        "thaw_node",
        "run_node_checks",
        "collect_node_sysreport",
        "push_node_asset",
        "push_node_disks",
        "push_node_stats",
        "pull_node_config",
        "push_node_config",
        "create_node",
        "delete_node",
        "snooze_node_notifications",
        "unsnooze_node_notifications",
        "update_node_properties",
    }:
        schema = tools_by_name[name].parameters
        request_ref = schema["properties"]["request"]["$ref"]
        request_schema = schema["$defs"][request_ref.rsplit("/", 1)[-1]]
        confirmation_ref = request_schema["properties"]["confirmation"]["$ref"]
        confirmation_schema = schema["$defs"][confirmation_ref.rsplit("/", 1)[-1]]

        assert "confirmation" in request_schema["required"]
        assert confirmation_schema["properties"]["phrase"]["minLength"] == 1
        assert "latest user message" in confirmation_schema["properties"]["phrase"]["description"]


async def test_default_tool_listing_exposes_bm25_search_tools(mcp_client):
    tools = await mcp_client.list_tools()
    tool_names = {tool.name for tool in tools}

    assert tool_names == {"search_tools", "call_tool"}


async def test_bm25_search_finds_node_inventory_stats(mcp_client):
    result = await mcp_client.call_tool(
        "search_tools",
        {"query": "node inventory statistics summary distribution"},
    )

    matches = result.structured_content["result"]
    match_names = [match["name"] for match in matches]

    assert len(matches) <= 10
    assert match_names[0] == "get_nodes_inventory_stats"


async def test_validation_error_includes_called_tool_schema(mcp_client):
    try:
        await mcp_client.call_tool(
            "get_cluster_nodes",
            {"cluster": "lab-cluster-a"},
        )
    except Exception as exc:
        message = str(exc)
    else:
        raise AssertionError("expected invalid tool arguments to raise")

    assert "tool" in message
    assert "get_cluster_nodes" in message
    assert "expected_input_schema" in message
    assert "request" in message
    assert "cluster_name" in message


async def test_proxy_validation_error_includes_target_tool_schema(mcp_client):
    try:
        await mcp_client.call_tool(
            "call_tool",
            {
                "name": "get_cluster_nodes",
                "arguments": {"cluster": "lab-cluster-a"},
            },
        )
    except Exception as exc:
        message = str(exc)
    else:
        raise AssertionError("expected invalid proxied tool arguments to raise")

    assert "tool" in message
    assert "get_cluster_nodes" in message
    assert "expected_input_schema" in message
    assert "request" in message
    assert "cluster_name" in message


async def test_unknown_tool_error_does_not_include_input_schema(mcp_client):
    try:
        await mcp_client.call_tool(
            "get_node_typo",
            {"request": {"nodename": "lab-node-01"}},
        )
    except Exception as exc:
        message = str(exc)
    else:
        raise AssertionError("expected unknown tool to raise")

    assert "Unknown tool" in message
    assert "expected_input_schema" not in message


async def test_malformed_call_tool_proxy_returns_call_tool_schema(mcp_client):
    try:
        await mcp_client.call_tool(
            "call_tool",
            {
                "tool_name": "get_node",
                "arguments": {"request": {"nodename": "lab-node-01"}},
            },
        )
    except Exception as exc:
        message = str(exc)
    else:
        raise AssertionError("expected malformed call_tool arguments to raise")

    assert "Invalid tool arguments" in message
    assert "expected_input_schema" in message
    assert "call_tool" in message
    assert "tool_name" in message
    assert "\"name\"" in message


async def test_proxy_target_tool_invalid_args_returns_target_tool_schema(mcp_client):
    try:
        await mcp_client.call_tool(
            "call_tool",
            {
                "name": "get_node",
                "arguments": {"name": "lab-node-01"},
            },
        )
    except Exception as exc:
        message = str(exc)
    else:
        raise AssertionError("expected invalid proxied target arguments to raise")

    assert "Invalid tool arguments" in message
    assert "expected_input_schema" in message
    assert "get_node" in message
    assert "request" in message
    assert "nodename" in message

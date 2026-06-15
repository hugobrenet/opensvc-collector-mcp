import pytest

from opensvc_collector_mcp.core.prechecks import (
    clean_selectors,
    clean_value,
    require_at_least_one_selector,
    require_exactly_one_selector,
    require_identity,
    require_match,
    require_single_row,
)


def test_clean_value_normalizes_optional_selector_values():
    assert clean_value(None) == ""
    assert clean_value(" node-a ") == "node-a"
    assert clean_value(42) == "42"


def test_clean_selectors_preserves_selector_names():
    assert clean_selectors({"node_id": " node-1 ", "nodename": None}) == {
        "node_id": "node-1",
        "nodename": "",
    }


def test_require_exactly_one_selector_returns_cleaned_values():
    selectors = require_exactly_one_selector(
        "delete node",
        {"node_id": " node-1 ", "nodename": None},
        selector_kind="node",
    )

    assert selectors == {"node_id": "node-1", "nodename": ""}


@pytest.mark.parametrize(
    "selectors",
    [
        {"node_id": None, "nodename": ""},
        {"node_id": "node-1", "nodename": "node-a"},
    ],
)
def test_require_exactly_one_selector_rejects_missing_or_multiple_values(selectors):
    with pytest.raises(
        ValueError,
        match="delete node requires exactly one node selector: node_id or nodename",
    ):
        require_exactly_one_selector(
            "delete node",
            selectors,
            selector_kind="node",
        )


def test_require_at_least_one_selector_accepts_correlated_values():
    selectors = require_at_least_one_selector(
        "attach tag to node",
        {"tag_id": "tag-1", "tag_name": " mcp-test-tag "},
        selector_kind="tag",
    )

    assert selectors == {"tag_id": "tag-1", "tag_name": "mcp-test-tag"}


def test_require_at_least_one_selector_uses_custom_error_message():
    with pytest.raises(
        ValueError,
        match="attach tag to node requires tag_id or tag_name",
    ):
        require_at_least_one_selector(
            "attach tag to node",
            {"tag_id": None, "tag_name": ""},
            message="attach tag to node requires tag_id or tag_name",
        )


def test_require_single_row_returns_only_row():
    row = require_single_row(
        {"data": [{"tag_id": "tag-1"}]},
        not_found_message="tag not found",
        multiple_message="tag ambiguous",
        invalid_message="tag payload invalid",
    )

    assert row == {"tag_id": "tag-1"}


def test_require_single_row_filters_exact_match_when_requested():
    row = require_single_row(
        {
            "data": [
                {"tag_id": "tag-1", "tag_name": "mcp-test-tag"},
                {"tag_id": "tag-2", "tag_name": "other-tag"},
            ]
        },
        not_found_message="tag not found",
        multiple_message="tag ambiguous",
        invalid_message="tag payload invalid",
        exact_match_field="tag_name",
        exact_match_value="mcp-test-tag",
    )

    assert row == {"tag_id": "tag-1", "tag_name": "mcp-test-tag"}


@pytest.mark.parametrize(
    ("response", "message"),
    [
        ({"data": []}, "tag not found"),
        ({"data": None}, "tag not found"),
        ({"data": [{"tag_id": "tag-1"}, {"tag_id": "tag-2"}]}, "tag ambiguous"),
        ({"data": ["not-a-dict"]}, "tag payload invalid"),
    ],
)
def test_require_single_row_rejects_absent_multiple_or_invalid_rows(
    response,
    message,
):
    with pytest.raises(ValueError, match=message):
        require_single_row(
            response,
            not_found_message="tag not found",
            multiple_message="tag ambiguous",
            invalid_message="tag payload invalid",
        )


def test_require_identity_returns_cleaned_id_and_name():
    resolved_id, resolved_name = require_identity(
        {"node_id": " node-1 ", "nodename": " lab-node-01 "},
        operation="attach tag to node",
        target="node",
        id_field="node_id",
        name_field="nodename",
    )

    assert resolved_id == "node-1"
    assert resolved_name == "lab-node-01"


@pytest.mark.parametrize(
    "row, message",
    [
        ({"node_id": "", "nodename": "node-a"}, "resolved node has no node_id"),
        ({"node_id": "node-1", "nodename": ""}, "resolved node has no nodename"),
    ],
)
def test_require_identity_rejects_missing_identity_fields(row, message):
    with pytest.raises(ValueError, match=message):
        require_identity(
            row,
            operation="delete node",
            target="node",
            id_field="node_id",
            name_field="nodename",
        )


def test_require_match_allows_empty_expected_value_and_matching_values():
    require_match(None, "resolved", message="must match")
    require_match(" node-a ", "node-a", message="must match")


def test_require_match_rejects_mismatch():
    with pytest.raises(ValueError, match="nodename must match the resolved node_id"):
        require_match(
            "node-b",
            "node-a",
            message="nodename must match the resolved node_id",
        )

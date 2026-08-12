import pytest

from opensvc_collector_mcp.core.collection import (
    collection_params,
    parse_collector_filters,
)


def test_parse_collector_filters_supports_dict_and_string_inputs():
    assert parse_collector_filters(
        {" app ": " APP-A ", "empty": "", "": "value"}
    ) == [("app", "APP-A")]
    assert parse_collector_filters("app=APP-A, status = up=ready") == [
        ("app", "APP-A"),
        ("status", "up=ready"),
    ]
    assert parse_collector_filters(None) == []


@pytest.mark.parametrize("filters", ["invalid", "=value", "field="])
def test_parse_collector_filters_rejects_invalid_string_items(filters):
    with pytest.raises(ValueError):
        parse_collector_filters(filters)


def test_collection_params_clamps_pagination_and_preserves_repeated_filters():
    assert collection_params(
        filters=[("app", "APP-A"), ("status", "up")],
        props="id,app",
        orderby="app",
        search="APP",
        limit=5000,
        offset=-10,
    ) == [
        ("limit", 1000),
        ("offset", 0),
        ("props", "id,app"),
        ("orderby", "app"),
        ("search", "APP"),
        ("filters", "app=APP-A"),
        ("filters", "status=up"),
    ]

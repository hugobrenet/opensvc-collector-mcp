from opensvc_collector_mcp.core import enrichment


async def test_get_nodenames_by_node_ids_deduplicates_and_ignores_missing_rows(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [
            {"data": [{"node_id": "1", "nodename": "node-a"}]},
            {"data": []},
        ]
    )
    monkeypatch.setattr(enrichment, "collector_get", collector.get)

    result = await enrichment.get_nodenames_by_node_ids(["2", " 1 ", "2", ""])

    assert result == {"1": "node-a"}
    assert [call.path for call in collector.calls] == ["/nodes", "/nodes"]
    assert collector.calls[0].param_values("filters") == ["node_id=1"]
    assert collector.calls[1].param_values("filters") == ["node_id=2"]


async def test_get_svcnames_by_svc_ids_resolves_unique_service_ids(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [{"data": [{"svc_id": "7", "svcname": "svc-a"}]}]
    )
    monkeypatch.setattr(enrichment, "collector_get", collector.get)

    result = await enrichment.get_svcnames_by_svc_ids([" 7 ", "7"])

    assert result == {"7": "svc-a"}
    assert collector.calls[0].path == "/services"
    assert collector.calls[0].param_values("filters") == ["svc_id=7"]


def test_enrich_rows_adds_names_without_mutating_source_rows():
    rows = [
        {"node_id": 1, "svc_id": "7", "status": "up"},
        {"node_id": 2, "svc_id": "8", "status": "down"},
    ]

    with_nodes = enrichment.enrich_rows_with_nodenames(rows, {"1": "node-a"})
    enriched = enrichment.enrich_rows_with_svcnames(with_nodes, {"7": "svc-a"})

    assert rows == [
        {"node_id": 1, "svc_id": "7", "status": "up"},
        {"node_id": 2, "svc_id": "8", "status": "down"},
    ]
    assert enriched == [
        {
            "node_id": 1,
            "nodename": "node-a",
            "svc_id": "7",
            "svcname": "svc-a",
            "status": "up",
        },
        {"node_id": 2, "svc_id": "8", "status": "down"},
    ]

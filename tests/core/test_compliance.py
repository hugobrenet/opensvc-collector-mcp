from opensvc_collector_mcp.core.compliance import _runs as runs
from opensvc_collector_mcp.core.compliance import status


async def test_compliance_status_returns_one_compact_page(
    monkeypatch,
    collector_mock_factory,
):
    collector = collector_mock_factory(
        [
            {
                "pagination": {
                    "limit": 2,
                    "offset": 4,
                    "returned": 2,
                    "next_offset": 6,
                    "complete": False,
                    "truncated": False,
                },
                "data": [
                    {
                        "id": 2,
                        "node_id": "NODE-ID",
                        "nodename": "node-a",
                        "run_module": "module.ok",
                        "run_status": 0,
                    },
                    {
                        "id": 1,
                        "svc_id": "SERVICE-ID",
                        "svcname": "svc-a",
                        "run_module": "module.failed",
                        "run_status": 1,
                    },
                ],
            }
        ]
    )
    monkeypatch.setattr(runs, "collector_get_page", collector.get)

    response = await status.get_compliance_status(
        run_status=1,
        orderby="~run_date",
        limit=2,
        offset=4,
    )

    assert response["pagination"]["next_offset"] == 6
    assert response["summary"] == {
        "ok_count": 1,
        "error_count": 1,
        "unknown_count": 0,
        "failed_modules": ["module.failed"],
    }
    assert "meta" not in response
    call = collector.calls[0]
    assert call.path == "/compliance/status"
    assert call.single_param("limit") == 2
    assert call.single_param("offset") == 4
    assert call.single_param("orderby") == "~run_date"
    assert call.param_values("filters") == ["comp_status.run_status=1"]

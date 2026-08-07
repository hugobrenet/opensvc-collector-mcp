import pytest

from opensvc_collector_mcp.core.nodes import _common as node_common
from opensvc_collector_mcp.core.services import _common as service_common
from opensvc_collector_mcp.core.tags import inventory
from opensvc_collector_mcp.core.tags import _common as tag_common


class CollectorPostRecorder:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def __call__(self, path, data=None, params=None):
        self.calls.append({"path": path, "data": data, "params": params})
        return self.response


class CollectorGetByPathRecorder:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    async def __call__(self, path, params=None):
        self.calls.append({"path": path, "params": params})
        try:
            return self.responses[path]
        except KeyError as exc:
            raise AssertionError(f"unexpected collector_get path: {path}") from exc


class CollectorDeleteRecorder:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def __call__(self, path, data=None, params=None):
        self.calls.append({"path": path, "data": data, "params": params})
        return self.response


async def test_create_tag_posts_writable_tag_fields(monkeypatch):
    recorder = CollectorPostRecorder(
        {
            "meta": {"count": 1},
            "data": [
                {
                    "tag_id": "tag-1",
                    "tag_name": "mcp-test-tag",
                    "tag_data": "created by test",
                    "tag_exclude": None,
                }
            ],
        }
    )
    monkeypatch.setattr(inventory, "collector_post", recorder)

    response = await inventory.create_tag(
        tag_name=" mcp-test-tag ",
        tag_data="created by test",
    )

    assert response["data"][0]["tag_name"] == "mcp-test-tag"
    assert recorder.calls == [
        {
            "path": "/tags",
            "data": {"tag_name": "mcp-test-tag", "tag_data": "created by test"},
            "params": None,
        }
    ]


async def test_create_tag_rejects_empty_tag_name(monkeypatch):
    recorder = CollectorPostRecorder({"meta": {}, "data": []})
    monkeypatch.setattr(inventory, "collector_post", recorder)

    with pytest.raises(ValueError, match="tag_name must not be empty"):
        await inventory.create_tag(tag_name="   ")

    assert recorder.calls == []


async def test_delete_tag_snapshots_and_deletes_by_tag_id(monkeypatch):
    get_recorder = CollectorGetByPathRecorder(
        {
            "/tags/tag-1": {
                "data": [
                    {
                        "tag_id": "tag-1",
                        "tag_name": "mcp-test-tag",
                        "tag_exclude": None,
                    }
                ],
            },
        }
    )
    delete_recorder = CollectorDeleteRecorder({"meta": {"count": 1}, "data": []})
    monkeypatch.setattr(tag_common, "collector_get", get_recorder)
    monkeypatch.setattr(inventory, "collector_delete", delete_recorder)

    response = await inventory.delete_tag(
        tag_id=" tag-1 ",
    )

    assert response["deleted"] is True
    assert response["tag_id"] == "tag-1"
    assert response["tag_name"] == "mcp-test-tag"
    assert response["tag"]["tag_name"] == "mcp-test-tag"
    assert response["collector_response"] == {"meta": {"count": 1}, "data": []}
    assert get_recorder.calls == [
        {
            "path": "/tags/tag-1",
            "params": {"props": "tag_id,tag_name,tag_exclude,tag_created,tag_data"},
        }
    ]
    assert delete_recorder.calls == [
        {"path": "/tags/tag-1", "data": None, "params": None}
    ]


async def test_delete_tag_resolves_tag_name_and_deletes_by_tag_id(monkeypatch):
    get_recorder = CollectorGetByPathRecorder(
        {
            "/tags": {
                "data": [
                    {
                        "tag_id": "tag-1",
                        "tag_name": "mcp-test-tag",
                        "tag_exclude": None,
                    }
                ],
            },
        }
    )
    delete_recorder = CollectorDeleteRecorder({"meta": {"count": 1}, "data": []})
    monkeypatch.setattr(tag_common, "collector_get", get_recorder)
    monkeypatch.setattr(inventory, "collector_delete", delete_recorder)

    response = await inventory.delete_tag(
        tag_name=" mcp-test-tag ",
    )

    assert response["deleted"] is True
    assert response["tag_id"] == "tag-1"
    assert response["tag_name"] == "mcp-test-tag"
    assert response["meta"]["selector"] == "tag_name"
    assert get_recorder.calls[0]["path"] == "/tags"
    params = get_recorder.calls[0]["params"]
    assert ("filters", "tag_name=mcp-test-tag") in params
    assert ("limit", 2) in params
    assert delete_recorder.calls == [
        {"path": "/tags/tag-1", "data": None, "params": None}
    ]


async def test_delete_tag_quotes_tag_id_path(monkeypatch):
    get_recorder = CollectorGetByPathRecorder(
        {
            "/tags/tag%2F1": {
                "data": [{"tag_id": "tag/1", "tag_name": "mcp-test-tag"}],
            },
        }
    )
    delete_recorder = CollectorDeleteRecorder({"meta": {"count": 1}, "data": []})
    monkeypatch.setattr(tag_common, "collector_get", get_recorder)
    monkeypatch.setattr(inventory, "collector_delete", delete_recorder)

    response = await inventory.delete_tag(
        tag_id=" tag/1 ",
    )

    assert response["tag_id"] == "tag/1"
    assert get_recorder.calls == [
        {
            "path": "/tags/tag%2F1",
            "params": {"props": "tag_id,tag_name,tag_exclude,tag_created,tag_data"},
        }
    ]
    assert delete_recorder.calls == [
        {"path": "/tags/tag%2F1", "data": None, "params": None}
    ]


async def test_delete_tag_rejects_ambiguous_tag_id_snapshot(monkeypatch):
    get_recorder = CollectorGetByPathRecorder(
        {
            "/tags/tag-1": {
                "data": [
                    {"tag_id": "tag-1", "tag_name": "mcp-test-tag"},
                    {"tag_id": "tag-1", "tag_name": "mcp-test-tag-copy"},
                ],
            },
        }
    )
    delete_recorder = CollectorDeleteRecorder({"meta": {}, "data": []})
    monkeypatch.setattr(tag_common, "collector_get", get_recorder)
    monkeypatch.setattr(inventory, "collector_delete", delete_recorder)

    with pytest.raises(ValueError, match="tag_id resolved to multiple tags"):
        await inventory.delete_tag(
            tag_id="tag-1",
        )

    assert delete_recorder.calls == []


async def test_delete_tag_rejects_ambiguous_tag_name_before_delete(monkeypatch):
    get_recorder = CollectorGetByPathRecorder(
        {
            "/tags": {
                "data": [
                    {"tag_id": "tag-1", "tag_name": "mcp-test-tag"},
                    {"tag_id": "tag-2", "tag_name": "mcp-test-tag"},
                ],
            },
        }
    )
    delete_recorder = CollectorDeleteRecorder({"meta": {}, "data": []})
    monkeypatch.setattr(tag_common, "collector_get", get_recorder)
    monkeypatch.setattr(inventory, "collector_delete", delete_recorder)

    with pytest.raises(ValueError, match="tag_name is ambiguous: mcp-test-tag"):
        await inventory.delete_tag(
            tag_name="mcp-test-tag",
        )

    assert delete_recorder.calls == []


async def test_delete_tag_rejects_tag_name_passed_as_tag_id(monkeypatch):
    get_recorder = CollectorGetByPathRecorder(
        {
            "/tags/mcp-test-tag": {
                "data": [{"tag_id": "tag-1", "tag_name": "mcp-test-tag"}],
            },
        }
    )
    delete_recorder = CollectorDeleteRecorder({"meta": {}, "data": []})
    monkeypatch.setattr(tag_common, "collector_get", get_recorder)
    monkeypatch.setattr(inventory, "collector_delete", delete_recorder)

    with pytest.raises(ValueError, match="tag_id selector did not resolve to the exact tag_id"):
        await inventory.delete_tag(
            tag_id="mcp-test-tag",
        )

    assert get_recorder.calls[0]["path"] == "/tags/mcp-test-tag"
    assert delete_recorder.calls == []

async def test_attach_tag_to_node_resolves_names_and_posts_ids(monkeypatch):
    tag_get_recorder = CollectorGetByPathRecorder(
        {
            "/tags": {
                "data": [
                    {
                        "tag_id": "tag-1",
                        "tag_name": "mcp-test-tag",
                    }
                ],
            },
        }
    )
    node_get_recorder = CollectorGetByPathRecorder(
        {
            "/nodes": {
                "data": [
                    {
                        "node_id": "node-1",
                        "nodename": "lab-node-01",
                        "status": "up",
                    }
                ],
            },
        }
    )
    post_recorder = CollectorPostRecorder({"info": "tag attached"})
    monkeypatch.setattr(tag_common, "collector_get", tag_get_recorder)
    monkeypatch.setattr(node_common, "collector_get", node_get_recorder)
    monkeypatch.setattr(inventory, "collector_post", post_recorder)

    response = await inventory.attach_tag_to_node(
        tag_name=" mcp-test-tag ",
        nodename=" lab-node-01 ",
        tag_attach_data="scope=lab",
    )

    assert response["attached"] is True
    assert response["tag_id"] == "tag-1"
    assert response["node_id"] == "node-1"
    assert response["tag_attach_data"] == "scope=lab"
    tag_params = tag_get_recorder.calls[0]["params"]
    node_params = node_get_recorder.calls[0]["params"]
    assert tag_get_recorder.calls[0]["path"] == "/tags"
    assert ("filters", "tag_name=mcp-test-tag") in tag_params
    assert ("limit", 2) in tag_params
    assert node_get_recorder.calls[0]["path"] == "/nodes"
    assert ("filters", "nodename=lab-node-01") in node_params
    assert ("limit", 2) in node_params
    assert post_recorder.calls == [
        {
            "path": "/tags/tag-1/nodes/node-1",
            "data": {"tag_attach_data": "scope=lab"},
            "params": None,
        }
    ]


async def test_attach_tag_to_node_quotes_ids_in_post_path(monkeypatch):
    tag_get_recorder = CollectorGetByPathRecorder(
        {
            "/tags/tag%2F1": {
                "data": [{"tag_id": "tag/1", "tag_name": "mcp-test-tag"}],
            },
        }
    )
    node_get_recorder = CollectorGetByPathRecorder(
        {
            "/nodes/node%2F1": {
                "data": [{"node_id": "node/1", "nodename": "lab-node-01"}],
            },
        }
    )
    post_recorder = CollectorPostRecorder({"info": "tag attached"})
    monkeypatch.setattr(tag_common, "collector_get", tag_get_recorder)
    monkeypatch.setattr(node_common, "collector_get", node_get_recorder)
    monkeypatch.setattr(inventory, "collector_post", post_recorder)

    response = await inventory.attach_tag_to_node(tag_id=" tag/1 ", node_id=" node/1 ")

    assert response["tag_id"] == "tag/1"
    assert response["node_id"] == "node/1"
    assert post_recorder.calls == [
        {"path": "/tags/tag%2F1/nodes/node%2F1", "data": None, "params": None}
    ]


async def test_attach_tag_to_node_accepts_correlated_ids_and_names(monkeypatch):
    tag_get_recorder = CollectorGetByPathRecorder(
        {
            "/tags/tag-1": {
                "data": [{"tag_id": "tag-1", "tag_name": "mcp-test-tag"}],
            },
        }
    )
    node_get_recorder = CollectorGetByPathRecorder(
        {
            "/nodes/node-1": {
                "data": [{"node_id": "node-1", "nodename": "lab-node-01"}],
            },
        }
    )
    post_recorder = CollectorPostRecorder({"info": "tag attached"})
    monkeypatch.setattr(tag_common, "collector_get", tag_get_recorder)
    monkeypatch.setattr(node_common, "collector_get", node_get_recorder)
    monkeypatch.setattr(inventory, "collector_post", post_recorder)

    response = await inventory.attach_tag_to_node(
        tag_id="tag-1",
        tag_name="mcp-test-tag",
        node_id="node-1",
        nodename="lab-node-01",
    )

    assert response["attached"] is True
    assert response["meta"]["tag_selector"] == "tag_id+tag_name"
    assert response["meta"]["node_selector"] == "node_id+nodename"
    assert tag_get_recorder.calls == [
        {
            "path": "/tags/tag-1",
            "params": {"props": "tag_id,tag_name,tag_exclude,tag_created,tag_data"},
        }
    ]
    assert node_get_recorder.calls == [
        {
            "path": "/nodes/node-1",
            "params": {
                "props": "node_id,nodename,status,updated,node_env,asset_env,"
                "team_responsible,loc_city"
            },
        }
    ]
    assert post_recorder.calls == [
        {"path": "/tags/tag-1/nodes/node-1", "data": None, "params": None}
    ]


async def test_attach_tag_to_node_rejects_correlated_name_mismatch(monkeypatch):
    tag_get_recorder = CollectorGetByPathRecorder(
        {
            "/tags/tag-1": {
                "data": [{"tag_id": "tag-1", "tag_name": "mcp-test-tag"}],
            },
        }
    )
    node_get_recorder = CollectorGetByPathRecorder(
        {
            "/nodes/node-1": {
                "data": [{"node_id": "node-1", "nodename": "lab-node-01"}],
            },
        }
    )
    post_recorder = CollectorPostRecorder({"info": "tag attached"})
    monkeypatch.setattr(tag_common, "collector_get", tag_get_recorder)
    monkeypatch.setattr(node_common, "collector_get", node_get_recorder)
    monkeypatch.setattr(inventory, "collector_post", post_recorder)

    with pytest.raises(ValueError, match="tag_name must match the resolved tag_id"):
        await inventory.attach_tag_to_node(
            tag_id="tag-1",
            tag_name="other-tag",
            node_id="node-1",
            nodename="lab-node-01",
        )

    assert post_recorder.calls == []


async def test_attach_tag_to_node_rejects_ambiguous_nodename_before_post(monkeypatch):
    tag_get_recorder = CollectorGetByPathRecorder(
        {
            "/tags/tag-1": {
                "data": [{"tag_id": "tag-1", "tag_name": "mcp-test-tag"}],
            },
        }
    )
    node_get_recorder = CollectorGetByPathRecorder(
        {
            "/nodes": {
                "data": [
                    {"node_id": "node-1", "nodename": "lab-node-01"},
                    {"node_id": "node-2", "nodename": "lab-node-01"},
                ],
            },
        }
    )
    post_recorder = CollectorPostRecorder({"info": "tag attached"})
    monkeypatch.setattr(tag_common, "collector_get", tag_get_recorder)
    monkeypatch.setattr(node_common, "collector_get", node_get_recorder)
    monkeypatch.setattr(inventory, "collector_post", post_recorder)

    with pytest.raises(ValueError, match="nodename is ambiguous: lab-node-01"):
        await inventory.attach_tag_to_node(tag_id="tag-1", nodename="lab-node-01")

    assert post_recorder.calls == []


async def test_attach_tag_to_service_resolves_names_and_posts_ids(monkeypatch):
    tag_get_recorder = CollectorGetByPathRecorder(
        {
            "/tags": {
                "data": [
                    {
                        "tag_id": "tag-1",
                        "tag_name": "mcp-test-tag",
                    }
                ],
            },
        }
    )
    service_get_recorder = CollectorGetByPathRecorder(
        {
            "/services": {
                "data": [
                    {
                        "svc_id": "svc-1",
                        "svcname": "svc/app/test",
                        "svc_status": "up",
                    }
                ],
            },
        }
    )
    post_recorder = CollectorPostRecorder({"info": "tag attached"})
    monkeypatch.setattr(tag_common, "collector_get", tag_get_recorder)
    monkeypatch.setattr(service_common, "collector_get", service_get_recorder)
    monkeypatch.setattr(inventory, "collector_post", post_recorder)

    response = await inventory.attach_tag_to_service(
        tag_name=" mcp-test-tag ",
        svcname=" svc/app/test ",
    )

    assert response["attached"] is True
    assert response["tag_id"] == "tag-1"
    assert response["svc_id"] == "svc-1"
    assert response["svcname"] == "svc/app/test"
    tag_params = tag_get_recorder.calls[0]["params"]
    service_params = service_get_recorder.calls[0]["params"]
    assert tag_get_recorder.calls[0]["path"] == "/tags"
    assert ("filters", "tag_name=mcp-test-tag") in tag_params
    assert ("limit", 2) in tag_params
    assert service_get_recorder.calls[0]["path"] == "/services"
    assert ("filters", "svcname=svc/app/test") in service_params
    assert ("limit", 2) in service_params
    assert post_recorder.calls == [
        {"path": "/tags/tag-1/services/svc-1", "data": None, "params": None}
    ]


async def test_attach_tag_to_service_quotes_ids_in_post_path(monkeypatch):
    tag_get_recorder = CollectorGetByPathRecorder(
        {
            "/tags/tag%2F1": {
                "data": [{"tag_id": "tag/1", "tag_name": "mcp-test-tag"}],
            },
        }
    )
    service_get_recorder = CollectorGetByPathRecorder(
        {
            "/services/svc%2F1": {
                "data": [{"svc_id": "svc/1", "svcname": "svc/app/test"}],
            },
        }
    )
    post_recorder = CollectorPostRecorder({"info": "tag attached"})
    monkeypatch.setattr(tag_common, "collector_get", tag_get_recorder)
    monkeypatch.setattr(service_common, "collector_get", service_get_recorder)
    monkeypatch.setattr(inventory, "collector_post", post_recorder)

    response = await inventory.attach_tag_to_service(
        tag_id=" tag/1 ",
        svc_id=" svc/1 ",
    )

    assert response["tag_id"] == "tag/1"
    assert response["svc_id"] == "svc/1"
    assert post_recorder.calls == [
        {"path": "/tags/tag%2F1/services/svc%2F1", "data": None, "params": None}
    ]


async def test_attach_tag_to_service_accepts_correlated_ids_and_names(monkeypatch):
    tag_get_recorder = CollectorGetByPathRecorder(
        {
            "/tags/tag-1": {
                "data": [{"tag_id": "tag-1", "tag_name": "mcp-test-tag"}],
            },
        }
    )
    service_get_recorder = CollectorGetByPathRecorder(
        {
            "/services/svc-1": {
                "data": [{"svc_id": "svc-1", "svcname": "svc/app/test"}],
            },
        }
    )
    post_recorder = CollectorPostRecorder({"info": "tag attached"})
    monkeypatch.setattr(tag_common, "collector_get", tag_get_recorder)
    monkeypatch.setattr(service_common, "collector_get", service_get_recorder)
    monkeypatch.setattr(inventory, "collector_post", post_recorder)

    response = await inventory.attach_tag_to_service(
        tag_id="tag-1",
        tag_name="mcp-test-tag",
        svc_id="svc-1",
        svcname="svc/app/test",
    )

    assert response["attached"] is True
    assert response["meta"]["tag_selector"] == "tag_id+tag_name"
    assert response["meta"]["service_selector"] == "svc_id+svcname"
    assert tag_get_recorder.calls == [
        {
            "path": "/tags/tag-1",
            "params": {"props": "tag_id,tag_name,tag_exclude,tag_created,tag_data"},
        }
    ]
    assert service_get_recorder.calls == [
        {
            "path": "/services/svc-1",
            "params": {
                "props": "svc_id,svcname,svc_app,svc_env,svc_status,"
                "svc_availstatus,svc_topology,updated"
            },
        }
    ]
    assert post_recorder.calls == [
        {"path": "/tags/tag-1/services/svc-1", "data": None, "params": None}
    ]


async def test_attach_tag_to_service_rejects_correlated_name_mismatch(monkeypatch):
    tag_get_recorder = CollectorGetByPathRecorder(
        {
            "/tags/tag-1": {
                "data": [{"tag_id": "tag-1", "tag_name": "mcp-test-tag"}],
            },
        }
    )
    service_get_recorder = CollectorGetByPathRecorder(
        {
            "/services/svc-1": {
                "data": [{"svc_id": "svc-1", "svcname": "svc/app/test"}],
            },
        }
    )
    post_recorder = CollectorPostRecorder({"info": "tag attached"})
    monkeypatch.setattr(tag_common, "collector_get", tag_get_recorder)
    monkeypatch.setattr(service_common, "collector_get", service_get_recorder)
    monkeypatch.setattr(inventory, "collector_post", post_recorder)

    with pytest.raises(ValueError, match="svcname must match the resolved svc_id"):
        await inventory.attach_tag_to_service(
            tag_id="tag-1",
            tag_name="mcp-test-tag",
            svc_id="svc-1",
            svcname="svc/app/other",
        )

    assert post_recorder.calls == []


async def test_attach_tag_to_service_rejects_ambiguous_svcname_before_post(
    monkeypatch,
):
    tag_get_recorder = CollectorGetByPathRecorder(
        {
            "/tags/tag-1": {
                "data": [{"tag_id": "tag-1", "tag_name": "mcp-test-tag"}],
            },
        }
    )
    service_get_recorder = CollectorGetByPathRecorder(
        {
            "/services": {
                "data": [
                    {"svc_id": "svc-1", "svcname": "svc/app/test"},
                    {"svc_id": "svc-2", "svcname": "svc/app/test"},
                ],
            },
        }
    )
    post_recorder = CollectorPostRecorder({"info": "tag attached"})
    monkeypatch.setattr(tag_common, "collector_get", tag_get_recorder)
    monkeypatch.setattr(service_common, "collector_get", service_get_recorder)
    monkeypatch.setattr(inventory, "collector_post", post_recorder)

    with pytest.raises(ValueError, match="svcname is ambiguous: svc/app/test"):
        await inventory.attach_tag_to_service(tag_id="tag-1", svcname="svc/app/test")

    assert post_recorder.calls == []


async def test_detach_tag_from_service_resolves_relation_and_deletes_ids(monkeypatch):
    tag_get_recorder = CollectorGetByPathRecorder(
        {
            "/tags": {
                "data": [
                    {
                        "tag_id": "tag-1",
                        "tag_name": "mcp-test-tag",
                    }
                ],
            },
        }
    )
    service_get_recorder = CollectorGetByPathRecorder(
        {
            "/services": {
                "data": [
                    {
                        "svc_id": "svc-1",
                        "svcname": "svc/app/test",
                        "svc_status": "up",
                    }
                ],
            },
        }
    )
    relation_get_recorder = CollectorGetByPathRecorder(
        {
            "/tags/tag-1/services": {
                "data": [
                    {
                        "svc_id": "svc-1",
                        "svcname": "svc/app/test",
                    }
                ],
            },
        }
    )
    delete_recorder = CollectorDeleteRecorder({"info": "tag detached"})
    monkeypatch.setattr(tag_common, "collector_get", tag_get_recorder)
    monkeypatch.setattr(service_common, "collector_get", service_get_recorder)
    monkeypatch.setattr(inventory, "collector_get", relation_get_recorder)
    monkeypatch.setattr(inventory, "collector_delete", delete_recorder)

    response = await inventory.detach_tag_from_service(
        tag_name=" mcp-test-tag ",
        svcname=" svc/app/test ",
    )

    assert response["detached"] is True
    assert response["tag_id"] == "tag-1"
    assert response["svc_id"] == "svc-1"
    assert response["relation"] == {"svc_id": "svc-1", "svcname": "svc/app/test"}
    relation_params = relation_get_recorder.calls[0]["params"]
    assert relation_get_recorder.calls[0]["path"] == "/tags/tag-1/services"
    assert ("filters", "svc_id=svc-1") in relation_params
    assert ("limit", 2) in relation_params
    assert delete_recorder.calls == [
        {"path": "/tags/tag-1/services/svc-1", "data": None, "params": None}
    ]


async def test_detach_tag_from_service_quotes_ids_in_delete_path(monkeypatch):
    tag_get_recorder = CollectorGetByPathRecorder(
        {
            "/tags/tag%2F1": {
                "data": [{"tag_id": "tag/1", "tag_name": "mcp-test-tag"}],
            },
        }
    )
    service_get_recorder = CollectorGetByPathRecorder(
        {
            "/services/svc%2F1": {
                "data": [{"svc_id": "svc/1", "svcname": "svc/app/test"}],
            },
        }
    )
    relation_get_recorder = CollectorGetByPathRecorder(
        {
            "/tags/tag%2F1/services": {
                "data": [{"svc_id": "svc/1", "svcname": "svc/app/test"}],
            },
        }
    )
    delete_recorder = CollectorDeleteRecorder({"info": "tag detached"})
    monkeypatch.setattr(tag_common, "collector_get", tag_get_recorder)
    monkeypatch.setattr(service_common, "collector_get", service_get_recorder)
    monkeypatch.setattr(inventory, "collector_get", relation_get_recorder)
    monkeypatch.setattr(inventory, "collector_delete", delete_recorder)

    response = await inventory.detach_tag_from_service(
        tag_id=" tag/1 ",
        svc_id=" svc/1 ",
    )

    assert response["tag_id"] == "tag/1"
    assert response["svc_id"] == "svc/1"
    assert delete_recorder.calls == [
        {"path": "/tags/tag%2F1/services/svc%2F1", "data": None, "params": None}
    ]


async def test_detach_tag_from_service_rejects_missing_relation_before_delete(
    monkeypatch,
):
    tag_get_recorder = CollectorGetByPathRecorder(
        {
            "/tags/tag-1": {
                "data": [{"tag_id": "tag-1", "tag_name": "mcp-test-tag"}],
            },
        }
    )
    service_get_recorder = CollectorGetByPathRecorder(
        {
            "/services/svc-1": {
                "data": [{"svc_id": "svc-1", "svcname": "svc/app/test"}],
            },
        }
    )
    relation_get_recorder = CollectorGetByPathRecorder(
        {"/tags/tag-1/services": {"data": []}}
    )
    delete_recorder = CollectorDeleteRecorder({"info": "tag detached"})
    monkeypatch.setattr(tag_common, "collector_get", tag_get_recorder)
    monkeypatch.setattr(service_common, "collector_get", service_get_recorder)
    monkeypatch.setattr(inventory, "collector_get", relation_get_recorder)
    monkeypatch.setattr(inventory, "collector_delete", delete_recorder)

    with pytest.raises(ValueError, match="relation not found"):
        await inventory.detach_tag_from_service(tag_id="tag-1", svc_id="svc-1")

    assert delete_recorder.calls == []


async def test_detach_tag_from_node_resolves_relation_and_deletes_ids(monkeypatch):
    tag_get_recorder = CollectorGetByPathRecorder(
        {
            "/tags": {
                "data": [
                    {
                        "tag_id": "tag-1",
                        "tag_name": "mcp-test-tag",
                    }
                ],
            },
        }
    )
    node_get_recorder = CollectorGetByPathRecorder(
        {
            "/nodes": {
                "data": [
                    {
                        "node_id": "node-1",
                        "nodename": "lab-node-01",
                        "status": "up",
                    }
                ],
            },
        }
    )
    relation_get_recorder = CollectorGetByPathRecorder(
        {
            "/tags/tag-1/nodes": {
                "data": [
                    {
                        "node_id": "node-1",
                        "nodename": "lab-node-01",
                    }
                ],
            },
        }
    )
    delete_recorder = CollectorDeleteRecorder({"info": "tag detached"})
    monkeypatch.setattr(tag_common, "collector_get", tag_get_recorder)
    monkeypatch.setattr(node_common, "collector_get", node_get_recorder)
    monkeypatch.setattr(inventory, "collector_get", relation_get_recorder)
    monkeypatch.setattr(inventory, "collector_delete", delete_recorder)

    response = await inventory.detach_tag_from_node(
        tag_name=" mcp-test-tag ",
        nodename=" lab-node-01 ",
    )

    assert response["detached"] is True
    assert response["tag_id"] == "tag-1"
    assert response["node_id"] == "node-1"
    assert response["relation"] == {"node_id": "node-1", "nodename": "lab-node-01"}
    relation_params = relation_get_recorder.calls[0]["params"]
    assert relation_get_recorder.calls[0]["path"] == "/tags/tag-1/nodes"
    assert ("filters", "node_id=node-1") in relation_params
    assert ("limit", 2) in relation_params
    assert delete_recorder.calls == [
        {"path": "/tags/tag-1/nodes/node-1", "data": None, "params": None}
    ]


async def test_detach_tag_from_node_quotes_ids_in_delete_path(monkeypatch):
    tag_get_recorder = CollectorGetByPathRecorder(
        {
            "/tags/tag%2F1": {
                "data": [{"tag_id": "tag/1", "tag_name": "mcp-test-tag"}],
            },
        }
    )
    node_get_recorder = CollectorGetByPathRecorder(
        {
            "/nodes/node%2F1": {
                "data": [{"node_id": "node/1", "nodename": "lab-node-01"}],
            },
        }
    )
    relation_get_recorder = CollectorGetByPathRecorder(
        {
            "/tags/tag%2F1/nodes": {
                "data": [{"node_id": "node/1", "nodename": "lab-node-01"}],
            },
        }
    )
    delete_recorder = CollectorDeleteRecorder({"info": "tag detached"})
    monkeypatch.setattr(tag_common, "collector_get", tag_get_recorder)
    monkeypatch.setattr(node_common, "collector_get", node_get_recorder)
    monkeypatch.setattr(inventory, "collector_get", relation_get_recorder)
    monkeypatch.setattr(inventory, "collector_delete", delete_recorder)

    response = await inventory.detach_tag_from_node(tag_id=" tag/1 ", node_id=" node/1 ")

    assert response["tag_id"] == "tag/1"
    assert response["node_id"] == "node/1"
    assert delete_recorder.calls == [
        {"path": "/tags/tag%2F1/nodes/node%2F1", "data": None, "params": None}
    ]


async def test_detach_tag_from_node_rejects_missing_relation_before_delete(monkeypatch):
    tag_get_recorder = CollectorGetByPathRecorder(
        {
            "/tags/tag-1": {
                "data": [{"tag_id": "tag-1", "tag_name": "mcp-test-tag"}],
            },
        }
    )
    node_get_recorder = CollectorGetByPathRecorder(
        {
            "/nodes/node-1": {
                "data": [{"node_id": "node-1", "nodename": "lab-node-01"}],
            },
        }
    )
    relation_get_recorder = CollectorGetByPathRecorder(
        {"/tags/tag-1/nodes": {"data": []}}
    )
    delete_recorder = CollectorDeleteRecorder({"info": "tag detached"})
    monkeypatch.setattr(tag_common, "collector_get", tag_get_recorder)
    monkeypatch.setattr(node_common, "collector_get", node_get_recorder)
    monkeypatch.setattr(inventory, "collector_get", relation_get_recorder)
    monkeypatch.setattr(inventory, "collector_delete", delete_recorder)

    with pytest.raises(ValueError, match="relation not found"):
        await inventory.detach_tag_from_node(tag_id="tag-1", node_id="node-1")

    assert delete_recorder.calls == []

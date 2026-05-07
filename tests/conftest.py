from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import pytest
from fastmcp import Client

from opensvc_collector_mcp.server import mcp


@dataclass(frozen=True)
class CollectorCall:
    path: str
    params: dict[str, Any] | Sequence[tuple[str, Any]] | None

    @property
    def param_items(self) -> list[tuple[str, Any]]:
        if self.params is None:
            return []
        if isinstance(self.params, dict):
            return list(self.params.items())
        return list(self.params)

    def param_values(self, key: str) -> list[Any]:
        return [value for item_key, value in self.param_items if item_key == key]

    def single_param(self, key: str) -> Any:
        values = self.param_values(key)
        if len(values) != 1:
            raise AssertionError(f"expected one {key!r} param, got {values!r}")
        return values[0]


class CollectorMock:
    def __init__(self, responses: list[dict[str, Any]] | None = None) -> None:
        self.calls: list[CollectorCall] = []
        self.responses = list(responses or [])

    async def get(
        self,
        path: str,
        params: dict[str, Any] | Sequence[tuple[str, Any]] | None = None,
    ) -> dict[str, Any]:
        self.calls.append(CollectorCall(path=path, params=params))
        if not self.responses:
            raise AssertionError(f"unexpected Collector GET {path!r} params={params!r}")
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


@pytest.fixture
async def mcp_client():
    async with Client(mcp) as client:
        yield client


@pytest.fixture
def collector_mock_factory():
    return CollectorMock

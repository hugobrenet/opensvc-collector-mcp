import asyncio

import pytest

from opensvc_collector_mcp.config import COLLECTOR_FANOUT_MAX_CONCURRENCY
from opensvc_collector_mcp.core.concurrency import bounded_map


async def test_bounded_map_preserves_input_order():
    async def worker(value: int) -> int:
        await asyncio.sleep((4 - value) / 1000)
        return value * 10

    result = await bounded_map([1, 2, 3], worker, max_concurrency=3)

    assert result == [10, 20, 30]


async def test_bounded_map_limits_active_workers():
    active = 0
    peak_active = 0

    async def worker(value: int) -> int:
        nonlocal active, peak_active
        active += 1
        peak_active = max(peak_active, active)
        try:
            await asyncio.sleep(0.001)
            return value
        finally:
            active -= 1

    result = await bounded_map(range(12), worker, max_concurrency=3)

    assert result == list(range(12))
    assert peak_active == 3


async def test_bounded_map_uses_shared_default_limit():
    active = 0
    peak_active = 0

    async def worker(value: int) -> int:
        nonlocal active, peak_active
        active += 1
        peak_active = max(peak_active, active)
        try:
            await asyncio.sleep(0.001)
            return value
        finally:
            active -= 1

    item_count = COLLECTOR_FANOUT_MAX_CONCURRENCY + 5
    result = await bounded_map(range(item_count), worker)

    assert result == list(range(item_count))
    assert peak_active == COLLECTOR_FANOUT_MAX_CONCURRENCY == 20


async def test_bounded_map_returns_empty_without_calling_worker():
    called = False

    async def worker(value: int) -> int:
        nonlocal called
        called = True
        return value

    assert await bounded_map([], worker) == []
    assert called is False


@pytest.mark.parametrize("max_concurrency", [0, -1])
async def test_bounded_map_rejects_invalid_max_concurrency(max_concurrency: int):
    async def worker(value: int) -> int:
        return value

    with pytest.raises(ValueError, match="greater than 0"):
        await bounded_map([1], worker, max_concurrency=max_concurrency)


async def test_bounded_map_cancels_other_workers_after_failure():
    blockers_started = asyncio.Event()
    release_blockers = asyncio.Event()
    started_blockers = 0
    cancelled: set[str] = set()
    started: set[str] = set()

    async def worker(value: str) -> str:
        nonlocal started_blockers
        started.add(value)
        if value == "failure":
            await blockers_started.wait()
            raise RuntimeError("worker failed")

        started_blockers += 1
        if started_blockers == 2:
            blockers_started.set()
        try:
            await release_blockers.wait()
        except asyncio.CancelledError:
            cancelled.add(value)
            raise
        return value

    try:
        with pytest.raises(RuntimeError, match="worker failed"):
            await bounded_map(
                ["blocker-a", "blocker-b", "failure", "not-started"],
                worker,
                max_concurrency=3,
            )
    finally:
        release_blockers.set()

    assert started == {"blocker-a", "blocker-b", "failure"}
    assert cancelled == {"blocker-a", "blocker-b"}

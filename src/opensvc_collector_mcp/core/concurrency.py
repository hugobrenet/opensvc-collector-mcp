import asyncio
from collections.abc import Awaitable, Callable, Iterable
from typing import TypeVar, cast

from opensvc_collector_mcp.config import COLLECTOR_FANOUT_MAX_CONCURRENCY


ItemT = TypeVar("ItemT")
ResultT = TypeVar("ResultT")


async def bounded_map(
    items: Iterable[ItemT],
    worker: Callable[[ItemT], Awaitable[ResultT]],
    *,
    max_concurrency: int = COLLECTOR_FANOUT_MAX_CONCURRENCY,
) -> list[ResultT]:
    """Apply an async worker with bounded concurrency and preserve input order."""
    if max_concurrency < 1:
        raise ValueError("max_concurrency must be greater than 0")

    values = list(items)
    if not values:
        return []

    queue = asyncio.Queue[tuple[int, ItemT]]()
    for indexed_item in enumerate(values):
        queue.put_nowait(indexed_item)

    results: list[object] = [None] * len(values)

    async def run_worker() -> None:
        while True:
            try:
                index, item = queue.get_nowait()
            except asyncio.QueueEmpty:
                return

            try:
                results[index] = await worker(item)
            finally:
                queue.task_done()

    tasks = [
        asyncio.create_task(run_worker())
        for _ in range(min(max_concurrency, len(values)))
    ]
    try:
        await asyncio.gather(*tasks)
    except BaseException:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise

    return cast(list[ResultT], results)

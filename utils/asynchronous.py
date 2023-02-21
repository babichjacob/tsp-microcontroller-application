from asyncio import CancelledError, create_task, wait, FIRST_COMPLETED
from typing import Any, Coroutine


async def at_least_one(coros: list[Coroutine[Any, Any, Any]]):
    """
    Wait until at least one of the coroutines finishes
    """

    tasks = [create_task(coro) for coro in coros]

    try:
        _done, pending = await wait(
            tasks,
            # Slight misnomer because more than one task can complete
            # in the same tick (synchronous section of code)
            return_when=FIRST_COMPLETED,
        )
    except CancelledError:
        for task in tasks:
            task.cancel()

        raise

    # But whichever didn’t complete will still be scheduled to run in the background
    # which is undesired, so cancel all those tasks:
    for task in pending:
        task.cancel()

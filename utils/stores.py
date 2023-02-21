from asyncio import AbstractEventLoop, Queue, TimerHandle
from datetime import timedelta
from functools import partial
from operator import lshift
from typing import Any, AsyncGenerator, Callable, Optional

from option_and_result import NONE, MatchesSome, Option
from store import Args, DerivedValue, Readable, Value, readable


def no_op():
    pass


def derived_with_time(
    stores: list[Readable[Any]],
    derivation: Callable[Args, DerivedValue],
    get_max_period: Callable[[], timedelta],
    *,
    loop: AbstractEventLoop,
) -> Readable[DerivedValue]:
    n = len(stores)

    def start(set_: Callable[[DerivedValue], None]):
        values: list[Optional[Any]] = [None] * n
        pending = sum(map(partial(lshift, 1), range(n)))

        timer_handle: Option[TimerHandle] = NONE()

        def calculate_then_set_and_delay_and_recurse():
            # TODO: deal with this
            result = derivation(*values)  # type: ignore
            set_(result)

            match timer_handle.take().to_matchable():
                case MatchesSome(handle):
                    handle.cancel()

            delay = get_max_period()
            timer_handle.insert(
                loop.call_later(
                    delay.total_seconds(), calculate_then_set_and_delay_and_recurse
                )
            )

        if n == 0:
            calculate_then_set_and_delay_and_recurse()

            return no_op

        def subscribe_to_store(i_store: tuple[int, Readable[Any]]):
            (i, store) = i_store

            def callback(value: Any):
                values[i] = value
                nonlocal pending
                if pending:
                    pending &= ~(1 << i)
                if not pending:
                    calculate_then_set_and_delay_and_recurse()

            unsubscribe = store.subscribe(callback)
            return unsubscribe

        unsubscribers: list[Callable[[], None]] = list(
            map(subscribe_to_store, enumerate(stores))
        )

        def stop():
            match timer_handle.take().to_matchable():
                case MatchesSome(handle):
                    handle.cancel()

            for unsubscribe in unsubscribers:
                unsubscribe()

        return stop

    return readable(None, start)  # type: ignore


# TODO: extract to store-tools package
def values(store: Readable[Value]) -> AsyncGenerator[Value, None]:
    queue = Queue()

    unsubscribe = store.subscribe(queue.put_nowait)

    async def generator():
        try:
            while True:
                yield await queue.get()
        finally:
            unsubscribe()

    return generator()

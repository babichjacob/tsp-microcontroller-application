from typing import Callable, Iterator, Iterable, TypeVar

from option_and_result import NONE, Option, Some


def average(numbers: Iterable[float]) -> Option[float]:
    total = 0.0
    count = 0

    for number in numbers:
        total += number
        count += 1

    if count == 0:
        return NONE()

    return Some(total / count)


T = TypeVar("T")
M = TypeVar("M")


def filter_map(
    iterable: Iterable[T], function: Callable[[T], Option[M]]
) -> Iterator[M]:
    for value in iterable:
        maybe = function(value)

        if maybe.is_some():
            yield maybe.unwrap()

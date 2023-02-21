from typing import Callable, Iterator, Iterable, TypeVar

from option_and_result import MatchesNone, MatchesSome, NONE, Option, Some


def average(numbers: Iterable[float]) -> Option[float]:
    total = 0.0
    count = 0

    for number in numbers:
        total += number
        count += 1

    match count:
        case 0:
            return NONE()
        case count_at_least_one:
            return Some(total / count_at_least_one)


T = TypeVar("T")
M = TypeVar("M")


def filter_map(
    iterable: Iterable[T], function: Callable[[T], Option[M]]
) -> Iterator[M]:
    for value in iterable:
        maybe = function(value)

        match maybe.to_matchable():
            case MatchesNone():
                pass
            case MatchesSome(some):
                yield some

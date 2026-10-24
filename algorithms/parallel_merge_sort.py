from concurrent.futures import ThreadPoolExecutor
from typing import Sequence, TypeVar

from .merge_sort import merge, merge_sort

T = TypeVar("T")


def parallel_merge_sort(
    arr: Sequence[T], max_workers: int = 4, cutoff: int = 2_048
) -> list[T]:
    """Sort using one bounded thread pool; small branches stay sequential."""
    if max_workers < 1:
        raise ValueError("max_workers must be at least 1")
    if cutoff < 2:
        raise ValueError("cutoff must be at least 2")
    values = list(arr)
    if len(values) < 2 or max_workers == 1 or len(values) < cutoff:
        return merge_sort(values)

    def sort_branch(items: list[T]) -> list[T]:
        if len(items) < 2 or len(items) < cutoff:
            return merge_sort(items)
        middle = len(items) // 2
        return merge(sort_branch(items[:middle]), sort_branch(items[middle:]))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        middle = len(values) // 2
        left_future = executor.submit(sort_branch, values[:middle])
        right = sort_branch(values[middle:])
        return merge(left_future.result(), right)

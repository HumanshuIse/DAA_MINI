from typing import Sequence, TypeVar

T = TypeVar("T")


def merge(left: Sequence[T], right: Sequence[T]) -> list[T]:
    """Stable merge that returns a new list."""
    result: list[T] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    return result + list(left[i:]) + list(right[j:])


def merge_sort(arr: Sequence[T]) -> list[T]:
    """Return a stable merge-sorted copy of arr."""
    if len(arr) < 2:
        return list(arr)
    middle = len(arr) // 2
    return merge(merge_sort(arr[:middle]), merge_sort(arr[middle:]))

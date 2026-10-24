from typing import Any, Sequence


def generate_sort_trace(arr: Sequence[int]) -> dict[str, Any]:
    """Create a bounded educational trace from the actual merge-sort process."""
    values = list(arr)
    steps: list[dict[str, Any]] = []
    comparisons = 0
    merges = 0
    limit = 900

    def snapshot(state: list[int], phase: str, left: list[int] | None = None,
                 right: list[int] | None = None, active: list[int] | None = None) -> None:
        if len(steps) < limit:
            steps.append({"array": state[:], "phase": phase, "left": left or [],
                          "right": right or [], "active": active or [],
                          "comparisons": comparisons, "merges": merges})

    def sort(items: list[int]) -> list[int]:
        nonlocal comparisons, merges
        if len(items) <= 1:
            snapshot(items, "base")
            return items
        middle = len(items) // 2
        left = sort(items[:middle])
        right = sort(items[middle:])
        snapshot(left + right, "split", left, right)
        result: list[int] = []
        i = j = 0
        while i < len(left) and j < len(right):
            comparisons += 1
            active = [left[i], right[j]]
            snapshot(result + left[i:] + right[j:], "compare", left, right, active)
            if left[i] <= right[j]:
                result.append(left[i]); i += 1
            else:
                result.append(right[j]); j += 1
            snapshot(result + left[i:] + right[j:], "choose", left, right, active)
        result.extend(left[i:]); result.extend(right[j:])
        merges += 1
        snapshot(result, "merge", left, right)
        return result

    sorted_values = sort(values)
    snapshot(sorted_values, "complete")
    return {"input": values, "sorted": sorted_values, "steps": steps,
            "comparisons": comparisons, "merges": merges}

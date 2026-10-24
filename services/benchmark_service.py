import statistics
import time
from typing import Any

from algorithms.merge_sort import merge_sort
from algorithms.parallel_merge_sort import parallel_merge_sort


def _median_ns(values: list[int]) -> int:
    return int(statistics.median(values))


def benchmark_sorting_algorithms(
    arr: list[int], repetitions: int = 3, max_workers: int = 4, cutoff: int = 2_048
) -> dict[str, Any]:
    if not 1 <= repetitions <= 10:
        raise ValueError("repetitions must be between 1 and 10")
    sequential_times: list[int] = []
    parallel_times: list[int] = []
    expected = sorted(arr)
    for trial in range(repetitions):
        first_parallel = trial % 2 == 1
        for parallel in ([True, False] if first_parallel else [False, True]):
            start = time.perf_counter_ns()
            result = parallel_merge_sort(arr, max_workers, cutoff) if parallel else merge_sort(arr)
            elapsed = time.perf_counter_ns() - start
            if result != expected:
                raise RuntimeError("sorting algorithm returned an incorrect result")
            (parallel_times if parallel else sequential_times).append(max(0, elapsed))
    single = _median_ns(sequential_times)
    parallel = _median_ns(parallel_times)
    speedup = single / parallel if parallel else None
    saved = ((single - parallel) / single * 100) if single else 0.0
    return {"single_time_ns": single, "parallel_time_ns": parallel,
            "speedup": speedup, "time_saved_percent": saved, "correct": True,
            "repetitions": repetitions}

from algorithms.merge_sort import merge_sort
from algorithms.parallel_merge_sort import parallel_merge_sort
from algorithms.trace_generator import generate_sort_trace


def test_merge_sort_edge_cases():
    for values in ([], [1], [3, 1, 2], [2, 2, -1], list(range(100, -1, -1))):
        assert merge_sort(values) == sorted(values)
        assert parallel_merge_sort(values, 1) == sorted(values)


def test_parallel_matches_sequential():
    values = [((i * 31) % 101) - 50 for i in range(1000)]
    assert parallel_merge_sort(values, 4, 32) == merge_sort(values)
    assert parallel_merge_sort(values, 4, 10000) == merge_sort(values)


def test_trace_is_real_and_complete():
    result = generate_sort_trace([4, 1, 3, 2])
    assert result["sorted"] == [1, 2, 3, 4]
    assert result["comparisons"] > 0 and result["merges"] > 0
    assert result["steps"][-1]["phase"] == "complete"

# MergeSort Arena

MergeSort Arena is a Flask-based DAA mini project that makes the comparison between classic and genuinely multithreaded merge sort interactive. It includes an actual Python trace generator, measured race, seeded benchmarks, SQLite history, CSV export, complexity explanations, and lightweight achievements.

## Run locally

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000/).

Run tests with `pytest`.

## Design

`algorithms/merge_sort.py` contains stable classic merge sort and the shared merge operation. `algorithms/parallel_merge_sort.py` reuses one bounded `ThreadPoolExecutor`; a cutoff keeps small branches sequential and avoids nested executor deadlocks. Python's GIL means CPU-bound threads can be slower, which is an intentional lesson of the race.

The benchmark uses `time.perf_counter_ns()` around sorting only, passes identical generated inputs, alternates execution order, validates against `sorted()` after timing, and stores medians plus reproducibility metadata in SQLite. The standard recurrence is `T(n) = 2T(n/2) + O(n)`, giving O(n log n) best, average, and worst-case work and O(n) auxiliary array space.

The UI is a responsive dark dashboard: Sorting Lab shows actual split/compare/merge events; Algorithm Race compares real measurements; Benchmark Arena stores experiments and exports CSV; Complexity Explorer covers theory; History and Achievements persist locally.

## Viva preparation

Merge sort is a stable divide-and-conquer algorithm: split, recursively sort, and merge. Its recurrence is `2T(n/2)+O(n)`, so each of log n levels does linear work. A thread pool schedules eligible branches, but the GIL and scheduling overhead can make parallel merge sort slower for CPU-bound Python workloads. Speedup is sequential time divided by parallel time. Auxiliary space is memory beyond the input required by the algorithm.

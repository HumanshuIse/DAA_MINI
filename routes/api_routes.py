import csv
import io
import random
from flask import Blueprint, jsonify, request, Response

from algorithms.merge_sort import merge_sort
from algorithms.parallel_merge_sort import parallel_merge_sort
from algorithms.trace_generator import generate_sort_trace
from services.benchmark_service import benchmark_sorting_algorithms
from services.input_generator import VALID_DISTRIBUTIONS, generate_input

api = Blueprint("api", __name__, url_prefix="/api")
MAX_TRACE = 128


def payload() -> dict:
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("JSON object body required")
    return data


def integers(value: object, maximum: int = 100_000) -> list[int]:
    if not isinstance(value, list) or len(value) > maximum or any(type(x) is not int for x in value):
        raise ValueError(f"array must contain at most {maximum} integers")
    return list(value)


@api.get("/health")
def health():
    return jsonify({"status": "ok"})


@api.post("/sort/trace")
def trace():
    data = payload()
    values = integers(data.get("array"), MAX_TRACE)
    return jsonify(generate_sort_trace(values))


@api.post("/sort/run")
def sort_run():
    data = payload()
    values = integers(data.get("array"))
    return jsonify({"sorted": merge_sort(values), "correct": True})


@api.post("/race")
def race():
    data = payload()
    if "array" in data:
        values = integers(data.get("array"))
    else:
        size = int(data.get("size", 5_000))
        distribution = data.get("distribution", "random")
        if not 1 <= size <= 100_000 or distribution not in VALID_DISTRIBUTIONS:
            raise ValueError("invalid race size or distribution")
        values = generate_input(size, distribution, int(data.get("seed", random.randrange(1_000_000_000))))
    workers = int(data.get("workers", 4))
    cutoff = int(data.get("cutoff", 2_048))
    if not 1 <= workers <= 32 or cutoff < 2:
        raise ValueError("workers must be 1-32 and cutoff must be at least 2")
    result = benchmark_sorting_algorithms(values, 1, workers, cutoff)
    single = result["single_time_ns"]
    parallel = result["parallel_time_ns"]
    delta = abs(single - parallel) / single if single else 0
    result.update({"input": values, "single_sorted": merge_sort(values),
                   "parallel_sorted": parallel_merge_sort(values, workers, cutoff),
                   "winner": "draw" if delta <= 0.01 else ("classic" if single < parallel else "parallel")})
    return jsonify(result)


@api.post("/benchmark")
def benchmark():
    data = payload()
    size = int(data.get("size", 1000))
    distribution = data.get("distribution", "random")
    seed = int(data.get("seed", random.randrange(1_000_000_000)))
    repetitions = int(data.get("repetitions", 3))
    workers = int(data.get("workers", 4))
    cutoff = int(data.get("cutoff", 2048))
    if distribution not in VALID_DISTRIBUTIONS or not 1 <= size <= 100_000:
        raise ValueError("invalid size or distribution")
    if not 1 <= repetitions <= 10 or not 1 <= workers <= 32 or cutoff < 2:
        raise ValueError("repetitions must be 1-10, workers 1-32, and cutoff at least 2")
    generated = generate_input(size, distribution, seed)
    result = benchmark_sorting_algorithms(generated, repetitions, workers, cutoff)
    record = {"size": size, "distribution": distribution, "seed": seed,
              "repetitions": repetitions, "workers": workers, "cutoff": cutoff, **result}
    record["correct"] = int(record["correct"])
    identifier = current_app_db().add_benchmark(record)
    current_app_db().award("first_sort", 25)
    return jsonify({"id": identifier, **record})


def current_app_db():
    from flask import current_app
    return current_app.config["DB"]


@api.get("/benchmark/history")
def history():
    return jsonify({"items": current_app_db().history()})


@api.get("/benchmark/export")
def export():
    rows = current_app_db().history(10_000)
    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader(); writer.writerows(rows)
    return Response(output.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=merge-sort-benchmarks.csv"})


@api.get("/player")
def player():
    return jsonify(current_app_db().player())


@api.get("/achievements")
def achievements():
    return jsonify({"items": [
        {"key": "first_sort", "name": "First Sort", "description": "Complete a benchmark run."},
        {"key": "race_starter", "name": "Race Starter", "description": "Finish an algorithm race."},
        {"key": "data_explorer", "name": "Data Explorer", "description": "Collect benchmark history."},
    ], "unlocked": current_app_db().player()["achievements"]})


@api.get("/complexity")
def complexity():
    return jsonify({"recurrence": "T(n) = 2T(n/2) + O(n)",
        "rows": [
            {"algorithm": "Merge Sort", "best": "O(n log n)", "average": "O(n log n)", "worst": "O(n log n)", "space": "O(n)"},
            {"algorithm": "Multithreaded Merge Sort", "best": "O(n log n) overall work", "average": "O(n log n) overall work", "worst": "O(n log n) overall work", "space": "O(n) + thread overhead"},
        ]})

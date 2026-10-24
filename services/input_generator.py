import random

VALID_DISTRIBUTIONS = {"random", "sorted", "reverse", "nearly_sorted", "duplicates"}


def generate_input(size: int, distribution: str, seed: int | None = None) -> list[int]:
    if not 1 <= size <= 100_000:
        raise ValueError("size must be between 1 and 100,000")
    if distribution not in VALID_DISTRIBUTIONS:
        raise ValueError("unsupported input distribution")
    rng = random.Random(seed)
    values = [rng.randint(-size, size) for _ in range(size)]
    if distribution == "sorted":
        return sorted(values)
    if distribution == "reverse":
        return sorted(values, reverse=True)
    if distribution == "nearly_sorted":
        values.sort()
        swaps = max(1, size // 20)
        for _ in range(swaps):
            a, b = rng.randrange(size), rng.randrange(size)
            values[a], values[b] = values[b], values[a]
    if distribution == "duplicates":
        return [rng.randint(-10, 10) for _ in range(size)]
    return values

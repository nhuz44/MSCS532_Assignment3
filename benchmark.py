"""Reproducible comparisons: same dataset and 7 independent timing trials.

Reports median elapsed milliseconds, not worst-case guarantees. Different
machines, Python versions and background workloads will change timings.
"""
from __future__ import annotations
import csv
import platform
import random
import statistics
import time
from pathlib import Path
from quicksort import randomized_quicksort, deterministic_quicksort

ROOT = Path(__file__).resolve().parent
SIZES = (250, 750, 1500, 3000)
DISTRIBUTIONS = ('Random', 'Sorted', 'Reverse sorted', 'Repeated values')
TRIALS = 7


def data_for(distribution: str, n: int) -> list[int]:
    if distribution == 'Sorted':
        return list(range(n))
    if distribution == 'Reverse sorted':
        return list(range(n, 0, -1))
    if distribution == 'Repeated values':
        gen = random.Random(7000 + n)
        return [gen.randrange(8) for _ in range(n)]
    gen = random.Random(9000 + n)
    return [gen.randrange(0, n * 20) for _ in range(n)]


def run() -> list[dict[str, str | int | float]]:
    rows = []
    for distribution in DISTRIBUTIONS:
        for n in SIZES:
            original = data_for(distribution, n)
            expected = sorted(original)
            for method, sorter in (
                ('Randomized Quicksort', randomized_quicksort),
                ('First-pivot Quicksort', deterministic_quicksort),
            ):
                durations = []
                for repetition in range(TRIALS):
                    rng = random.Random(100_000 + n * 11 + repetition)
                    start = time.perf_counter_ns()
                    result = sorter(original, rng) if method == 'Randomized Quicksort' else sorter(original)
                    elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
                    if result != expected:
                        raise AssertionError(f'{method} failed on {distribution}, n={n}')
                    durations.append(elapsed_ms)
                rows.append({
                    'algorithm': method, 'dataset': distribution, 'n': n,
                    'median_time_ms': round(statistics.median(durations), 4),
                    'min_time_ms': round(min(durations), 4),
                    'max_time_ms': round(max(durations), 4),
                    'trials': TRIALS,
                })
    dest = ROOT / 'benchmark_results.csv'
    with dest.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    meta = ROOT / 'environment.txt'
    meta.write_text(
        f'Platform: {platform.platform()}\nPython: {platform.python_version()}\n'
        f'Processor: {platform.processor() or "not reported"}\n'
        f'Timing: perf_counter_ns median of {TRIALS} runs; wall clock ms\n'
        'Input generated from fixed random seeds; pivot seeds vary by trial\n',
        encoding='utf-8',
    )
    print(f'Saved {len(rows)} rows to {dest.name}')
    print(meta.read_text())
    return rows


if __name__ == '__main__':
    run()

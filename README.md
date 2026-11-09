# MSCS532 Assignment 3 — Algorithm Efficiency and Scalability

**Course:** MSCS-532-B01: Algorithms and Data Structures  
**Assignment:** 3 — Understanding Algorithm Efficiency and Scalability

## Overview

This project compares randomized and first-element-pivot Quicksort and implements a separate-chaining hash table in Python. I measured sorting time on random, sorted, reverse-sorted, and repeated-value arrays and examined how the hash table's load-factor threshold affects collision chains.

## Files

| File | Purpose |
|---|---|
| `quicksort.py` | Randomized and deterministic Quicksort with the same three-way partitioning method |
| `chained_hash_table.py` | Integer-key hash table with chaining and dynamic resizing |
| `demo.py` | Small example of sorting and insert/search/update/delete |
| `test_algorithms.py` | Automated correctness and edge-case tests |
| `benchmark.py` | Sorting experiments (4 input types × 4 sizes × 2 algorithms) |
| `benchmark_results.csv` | Measured median runtimes (7 trials per case) |
| `hash_load_experiment.py` | Hash-table experiment using three load-factor thresholds |
| `hash_load_results.csv` | Hash-table collision and chain statistics |
| `generate_report.py` | Creates the chart and Word report directly from both CSV files |
| `quicksort_comparison.png` | Charts from the latest benchmark CSV |
| `Assignment3_Report.docx` | Written theoretical analysis and measured results |
| `environment.txt` | Machine and Python details for the latest sorting run |

## Run on macOS or Linux

Python 3.10 or newer is recommended. The sorting code, hash table, and tests use only Python's standard library.

```bash
python3 demo.py
python3 -m unittest discover -v
python3 benchmark.py
python3 hash_load_experiment.py
```

To generate the chart and Word report from **your own machine's results**, set up a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python generate_report.py
```

The generated report reads the CSV files rather than hardcoding measurements, helping keep its figures consistent with the posted data. The `.venv` directory is excluded from Git with `.gitignore`.

## What I found

Randomized pivots generally avoid the extreme slowdown that the first-pivot method can exhibit on reverse-sorted inputs. For repeated values, the shared three-way partitioner helps both approaches by grouping equal keys. On random arrays, pivot selection overhead and normal timing variation can make either implementation slightly faster in a given run.

The hash table supports insertion, lookup, updating an existing key, and deletion. Its default maximum load factor is 0.75. It automatically expands or contracts its bucket array to limit chain growth. Tests also verify collisions, missing keys, invalid keys, and rehashing.

Times in `benchmark_results.csv` are **wall-clock measurements from the environment identified in `environment.txt`**; they will differ across machines. I rerun the benchmarks before submitting updated results.

## Notes

- Quicksort returns a new ascending list, leaving its input unchanged.
- Hash-table keys are integers in the range `0 <= key < 2**61 - 1`.
- `search()` and `delete()` raise `KeyError` when the key is not present.
- Neither implementation is designed as a production-ready secure service.

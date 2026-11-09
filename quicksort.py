"""Two comparable iterative three-way Quicksort variants.

Both algorithms use exactly the same partitioner, differing only in how
pivots are selected. The randomized variant draws a uniform integer from
the current inclusive subarray. Returns a sorted copy; inputs are unchanged.
"""
from __future__ import annotations
import random
from typing import Sequence


def _quicksort(values: Sequence[int], randomized: bool, rng: random.Random | None) -> list[int]:
    items = list(values)
    if len(items) < 2:
        return items
    generator = rng if rng is not None else random.Random()
    pending: list[tuple[int, int]] = [(0, len(items) - 1)]
    while pending:
        low, high = pending.pop()
        if low >= high:
            continue
        # For the randomized version, *every* integer index in [low, high]
        # has equal probability of selection. The other version always uses low.
        pivot_index = generator.randrange(low, high + 1) if randomized else low
        pivot = items[pivot_index]
        lt, i, gt = low, low, high
        # Invariant: [low,lt) < pivot; [lt,i) == pivot; (gt,high] > pivot.
        while i <= gt:
            if items[i] < pivot:
                items[lt], items[i] = items[i], items[lt]
                lt += 1
                i += 1
            elif items[i] > pivot:
                items[i], items[gt] = items[gt], items[i]
                gt -= 1
            else:
                i += 1
        # Equal values [lt,gt] are already in their final group; never recurse.
        # Explicit stack avoids Python recursion-depth failures on ordered data.
        if low < lt - 1:
            pending.append((low, lt - 1))
        if gt + 1 < high:
            pending.append((gt + 1, high))
    return items


def randomized_quicksort(values: Sequence[int], rng: random.Random | None = None) -> list[int]:
    """Return ascending sorted copy using uniformly random pivots."""
    return _quicksort(values, randomized=True, rng=rng)


def deterministic_quicksort(values: Sequence[int]) -> list[int]:
    """Return ascending sorted copy using first-element pivots."""
    return _quicksort(values, randomized=False, rng=None)


if __name__ == '__main__':
    sample = [9, 2, 9, 5, 1, 8, 5]
    print('Original:', sample)
    print('Randomized Quicksort:', randomized_quicksort(sample, random.Random(42)))
    print('First-pivot Quicksort:', deterministic_quicksort(sample))

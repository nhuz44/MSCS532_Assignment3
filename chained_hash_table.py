"""Separate-chaining hash table for nonnegative integer keys < 2**61-1.

For each table, a and b are drawn from a Carter-Wegman-style affine
universal-hashing family, h(k)=((a*k+b) % p) % m. Buckets are Python lists.
The table grows and shrinks to manage load factor; keys stay within domain.
This is an educational hash table, *not* a cryptographic hash or a replacement
for Python's production dict.
"""
from __future__ import annotations
import random
from typing import Any

PRIME = 2**61 - 1


class ChainedHashTable:
    def __init__(self, capacity: int = 8, max_load_factor: float = 0.75,
                 seed: int | None = None):
        if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity < 2:
            raise ValueError('capacity must be an integer >= 2')
        if not 0.25 <= max_load_factor <= 10:
            raise ValueError('max_load_factor must be in [0.25, 10]')
        self._minimum_capacity = capacity
        self._buckets: list[list[tuple[int, Any]]] = [[] for _ in range(capacity)]
        self._count = 0
        self._threshold = max_load_factor
        rng = random.Random(seed)
        self._a = rng.randrange(1, PRIME)
        self._b = rng.randrange(0, PRIME)
        self.resize_count = 0

    @staticmethod
    def _validate_key(key: int) -> None:
        if isinstance(key, bool) or not isinstance(key, int) or not 0 <= key < PRIME:
            raise ValueError(f'key must be an integer between 0 and {PRIME - 1}')

    def _index(self, key: int) -> int:
        return ((self._a * key + self._b) % PRIME) % len(self._buckets)

    def _resize(self, new_capacity: int) -> None:
        original_buckets = self._buckets
        self._buckets = [[] for _ in range(new_capacity)]
        for bucket in original_buckets:
            for key, value in bucket:
                self._buckets[self._index(key)].append((key, value))
        self.resize_count += 1

    def insert(self, key: int, value: Any) -> None:
        """Add a pair, or replace the value of an existing key."""
        self._validate_key(key)
        bucket = self._buckets[self._index(key)]
        for i, (existing_key, _) in enumerate(bucket):
            if existing_key == key:
                bucket[i] = (key, value)
                return
        if (self._count + 1) / len(self._buckets) > self._threshold:
            self._resize(len(self._buckets) * 2)
            bucket = self._buckets[self._index(key)]
        bucket.append((key, value))
        self._count += 1

    def search(self, key: int) -> Any:
        """Return value, raising KeyError if missing (None is a valid value)."""
        self._validate_key(key)
        for existing_key, value in self._buckets[self._index(key)]:
            if existing_key == key:
                return value
        raise KeyError(key)

    def delete(self, key: int) -> Any:
        """Remove the key and return its value; raise KeyError if absent."""
        self._validate_key(key)
        bucket = self._buckets[self._index(key)]
        for i, (existing_key, value) in enumerate(bucket):
            if existing_key == key:
                bucket.pop(i)
                self._count -= 1
                if (len(self._buckets) > self._minimum_capacity
                        and self.load_factor < 0.20):
                    self._resize(max(self._minimum_capacity, len(self._buckets) // 2))
                return value
        raise KeyError(key)

    @property
    def load_factor(self) -> float:
        return self._count / len(self._buckets)

    @property
    def capacity(self) -> int:
        return len(self._buckets)

    def __len__(self) -> int:
        return self._count

    def stats(self) -> dict[str, int | float]:
        lengths = [len(bucket) for bucket in self._buckets]
        return {
            'items': len(self), 'slots': self.capacity,
            'load_factor': round(self.load_factor, 4),
            'collisions': sum(max(0, count - 1) for count in lengths),
            'max_chain_length': max(lengths, default=0),
            'resizes': self.resize_count,
        }


if __name__ == '__main__':
    table = ChainedHashTable(capacity=4, seed=2026)
    for key, value in [(120, 'queued'), (121, 'running'), (122, 'complete'), (123, 'queued')]:
        table.insert(key, value)
    print('Search 121:', table.search(121))
    print('Delete 120:', table.delete(120))
    print('After updates:', table.stats())

"""Correctness, collision, resizing and input-validation tests."""
import random
import unittest
from quicksort import randomized_quicksort, deterministic_quicksort
from chained_hash_table import ChainedHashTable, PRIME


class QuickSortTests(unittest.TestCase):
    def test_empty(self):
        for fn in (randomized_quicksort, deterministic_quicksort):
            self.assertEqual(fn([]), [])

    def test_one_item(self):
        for fn in (randomized_quicksort, deterministic_quicksort):
            self.assertEqual(fn([8]), [8])

    def test_sorted(self):
        values = list(range(200))
        for fn in (randomized_quicksort, deterministic_quicksort):
            self.assertEqual(fn(values), values)

    def test_reverse_sorted(self):
        values = list(range(200, 0, -1))
        for fn in (randomized_quicksort, deterministic_quicksort):
            self.assertEqual(fn(values), sorted(values))

    def test_repeated_values(self):
        values = [3, 1, 3, 5, 5, 2, 1, 5, 3]
        for fn in (randomized_quicksort, deterministic_quicksort):
            self.assertEqual(fn(values), sorted(values))

    def test_negatives(self):
        values = [-4, 0, -10, 23, -4]
        for fn in (randomized_quicksort, deterministic_quicksort):
            self.assertEqual(fn(values), sorted(values))

    def test_randomized_seeds_and_unmodified_input(self):
        values = [17, 4, 19, 4, 10, 2, 99, 4]
        for seed in range(20):
            self.assertEqual(randomized_quicksort(values, random.Random(seed)), sorted(values))
        self.assertEqual(values, [17, 4, 19, 4, 10, 2, 99, 4])

    def test_large_sorted_input_no_recursion_error(self):
        values = list(range(3500))
        self.assertEqual(deterministic_quicksort(values), values)


class HashTableTests(unittest.TestCase):
    def test_insert_search_delete(self):
        table = ChainedHashTable(seed=4)
        table.insert(101, 'pending')
        self.assertEqual(table.search(101), 'pending')
        self.assertEqual(table.delete(101), 'pending')
        with self.assertRaises(KeyError):
            table.search(101)

    def test_duplicate_key_updates_without_growth(self):
        table = ChainedHashTable(seed=4)
        table.insert(1, 'old')
        table.insert(1, 'new')
        self.assertEqual(len(table), 1)
        self.assertEqual(table.search(1), 'new')

    def test_none_is_valid_value(self):
        table = ChainedHashTable(seed=4)
        table.insert(1, None)
        self.assertIsNone(table.search(1))

    def test_missing_delete(self):
        with self.assertRaises(KeyError):
            ChainedHashTable().delete(99)

    def test_resizing_retains_entries(self):
        table = ChainedHashTable(capacity=2, seed=12)
        for key in range(400):
            table.insert(key, str(key))
            self.assertLessEqual(table.load_factor, 0.75)
        self.assertGreater(table.resize_count, 0)
        for key in range(400):
            self.assertEqual(table.search(key), str(key))
        for key in range(350):
            self.assertEqual(table.delete(key), str(key))
        self.assertEqual(len(table), 50)
        for key in range(350, 400):
            self.assertEqual(table.search(key), str(key))

    def test_collisions_resolved_by_chaining(self):
        table = ChainedHashTable(capacity=2, max_load_factor=10, seed=1)
        groups = {}
        for key in range(200):
            groups.setdefault(table._index(key), []).append(key)
        collided = next(group for group in groups.values() if len(group) >= 3)[:3]
        for key in collided:
            table.insert(key, f'value-{key}')
        self.assertGreaterEqual(table.stats()['collisions'], 2)
        self.assertTrue(all(table.search(key) == f'value-{key}' for key in collided))

    def test_invalid_keys(self):
        table = ChainedHashTable()
        for key in (-1, PRIME, 'store12', True, 3.1):
            with self.subTest(key=key), self.assertRaises(ValueError):
                table.insert(key, 'bad')

    def test_many_operations_match_dictionary(self):
        table = ChainedHashTable(capacity=4, seed=902)
        expected = {}
        gen = random.Random(456)
        for step in range(1200):
            key = gen.randrange(300)
            if gen.random() < 0.65:
                value = step
                table.insert(key, value)
                expected[key] = value
            else:
                if key in expected:
                    self.assertEqual(table.delete(key), expected.pop(key))
                else:
                    with self.assertRaises(KeyError):
                        table.delete(key)
        self.assertEqual(len(table), len(expected))
        for key, value in expected.items():
            self.assertEqual(table.search(key), value)


if __name__ == '__main__':
    unittest.main()

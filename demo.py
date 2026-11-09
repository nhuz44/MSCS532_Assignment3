"""Human-readable demonstrations of both assignment parts."""
from quicksort import randomized_quicksort, deterministic_quicksort
from chained_hash_table import ChainedHashTable
import random


def main() -> None:
    values = [8, 4, 8, -2, 10, 1, 4]
    print('SORT DEMONSTRATION')
    print('Original:', values)
    print('Randomized:', randomized_quicksort(values, random.Random(17)))
    print('First pivot:', deterministic_quicksort(values))
    print('\nHASH TABLE DEMONSTRATION')
    table = ChainedHashTable(capacity=4, seed=17)
    for key, status in [(1201, 'pending'), (1202, 'running'), (1203, 'done'), (1204, 'pending')]:
        table.insert(key, status)
    print('After insert:', table.stats())
    print('Search 1202:', table.search(1202))
    table.insert(1202, 'complete')
    print('Update 1202:', table.search(1202))
    print('Delete 1201:', table.delete(1201))
    print('Final:', table.stats())


if __name__ == '__main__':
    main()

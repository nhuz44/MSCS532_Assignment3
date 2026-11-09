"""Compare actual chain lengths at different configured load-factor thresholds."""
import csv
from pathlib import Path
from chained_hash_table import ChainedHashTable

ROOT = Path(__file__).resolve().parent


def main() -> None:
    rows = []
    for threshold in (0.50, 0.75, 2.00):
        table = ChainedHashTable(capacity=8, max_load_factor=threshold, seed=532)
        for key in range(3000):
            table.insert(key, f'store-{key}')
        for key in range(3000):
            assert table.search(key) == f'store-{key}'
        rows.append({'threshold': threshold, **table.stats()})
    with (ROOT / 'hash_load_results.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for row in rows:
        print(row)


if __name__ == '__main__':
    main()

# Pytest Evidence

Command:

```
PYTHONPATH=src pytest -q
```

Timestamp: 2026-02-03

Output:

```
.....                                                    [100%]
5 passed in 0.02s
```

Files exercised:

- `src/importer.py`
- `tests/test_importer.py`

Notes:

- Tests demonstrate deduplication behavior for CSV import scenarios.

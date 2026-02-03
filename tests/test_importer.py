import csv
import sys
from pathlib import Path

# Ensure `src` is on sys.path so tests can import the implementation
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from importer import import_transactions


def write_csv(path: Path, rows, headers=None):
    headers = headers or ["date", "transaction_id", "amount", "description"]
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def test_single_transaction(tmp_path):
    csv_file = tmp_path / "single.csv"
    rows = [{"date": "2026-02-01", "transaction_id": "TXN1", "amount": "100.00", "description": "Payment"}]
    write_csv(csv_file, rows)
    created = import_transactions(str(csv_file), account_id="acct-1")
    assert len(created) == 1
    assert created[0]["transaction_id"] == "TXN1"


def test_duplicate_rows_in_file(tmp_path):
    csv_file = tmp_path / "dup.csv"
    rows = [
        {"date": "2026-02-01", "transaction_id": "TXN2", "amount": "50.00", "description": "A"},
        {"date": "2026-02-01", "transaction_id": "TXN2", "amount": "50.00", "description": "A"},
    ]
    write_csv(csv_file, rows)
    created = import_transactions(str(csv_file), account_id="acct-1")
    assert len(created) == 1


def test_whitespace_and_case_normalization(tmp_path):
    csv_file = tmp_path / "norm.csv"
    rows = [
        {"date": "01/02/2026", "transaction_id": " TxN3 ", "amount": "10.00", "description": "x"},
        {"date": "2026-02-01", "transaction_id": "txn3", "amount": "10.00", "description": "x"},
    ]
    write_csv(csv_file, rows)
    created = import_transactions(str(csv_file), account_id="acct-1")
    assert len(created) == 1


def test_reimport_idempotent(tmp_path):
    csv_file = tmp_path / "reimp.csv"
    rows = [{"date": "2026-02-01", "transaction_id": "TXN4", "amount": "25.00", "description": "pay"}]
    write_csv(csv_file, rows)
    first = import_transactions(str(csv_file), account_id="acct-1")
    assert len(first) == 1
    # Simulate re-import using existing_transactions from first run
    second = import_transactions(str(csv_file), account_id="acct-1", existing_transactions=first)
    assert len(second) == 0


def test_close_timestamps_same_canonical_key(tmp_path):
    csv_file = tmp_path / "ts.csv"
    rows = [
        {"date": "2026-02-01", "transaction_id": "TXN5", "amount": "9.99", "description": "a"},
        {"date": "2026-02-01", "transaction_id": "TXN5", "amount": "9.9900", "description": "a"},
    ]
    write_csv(csv_file, rows)
    created = import_transactions(str(csv_file), account_id="acct-1")
    assert len(created) == 1

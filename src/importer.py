from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import csv


def _normalize_reference(ref: str) -> str:
    if ref is None:
        return ""
    return ref.strip().lower()


def _normalize_date(date_str: str) -> str:
    if not date_str:
        return ""
    # Try common date formats and normalize to ISO date
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date().isoformat()
        except Exception:
            continue
    # Fallback: return trimmed string
    return date_str.strip()


def _normalize_amount(amount_str: str) -> Decimal:
    try:
        d = Decimal(str(amount_str)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except Exception:
        d = Decimal("0.00")
    return d


def _canonical_key(account_id: str, reference: str, date: str, amount: Decimal) -> str:
    return f"{account_id}|{_normalize_reference(reference)}|{date}|{amount:.2f}"


def import_transactions(csv_path: str, account_id: str, existing_transactions=None):
    """
    Simulate importing transactions from a CSV file.

    CSV must have at least columns: date, transaction_id (or reference), amount, description

    Returns: list of created transactions (dicts)
    """
    if existing_transactions is None:
        existing_transactions = []

    existing_keys = set()
    for t in existing_transactions:
        key = _canonical_key(account_id, t.get("transaction_id") or t.get("reference"), t.get("date"), _normalize_amount(t.get("amount")))
        existing_keys.add(key)

    created = []
    with open(csv_path, newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            raw_ref = row.get("transaction_id") or row.get("reference") or ""
            raw_date = _normalize_date(row.get("date") or row.get("transaction_date") or "")
            raw_amount = _normalize_amount(row.get("amount") or row.get("amt") or "0")
            key = _canonical_key(account_id, raw_ref, raw_date, raw_amount)
            if key in existing_keys:
                continue
            tx = {
                "account_id": account_id,
                "transaction_id": raw_ref.strip() if raw_ref else "",
                "date": raw_date,
                "amount": f"{raw_amount:.2f}",
                "description": (row.get("description") or row.get("memo") or "").strip(),
            }
            created.append(tx)
            existing_keys.add(key)

    return created

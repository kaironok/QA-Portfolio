# Bug Report: Duplicate Transaction Import

## Overview

Importing bank statements creates duplicate transactions when the CSV contains repeated transaction references, causing incorrect account balances and reconciliation problems.

---

## Summary
- **Brief description:** Duplicate transactions are created when importing CSVs containing the same `transaction_id` or `bank_reference` more than once.

## Steps to Reproduce
1. Log into the application and navigate to `Accounts > Import Transactions`.
2. Upload a CSV containing two rows for the same transaction reference (identical `transaction_id` or `bank_reference`), matching amounts, and dates.
3. Map CSV columns (Date, Reference, Amount, Description) and click `Import`.
4. Open the affected account ledger and review the imported entries and account balance.

## Expected Behavior
- The importer should deduplicate transactions by a stable key (e.g., canonical `transaction_id`/`bank_reference` + date + amount) and only create one ledger entry.
- Account balance should reflect a single transaction.

## Actual Behavior
- Both rows are imported as separate transactions.
- Account balance is increased by the transaction amount twice.
- The ledger displays two identical entries with the same reference and timestamp.

## CSV Example
Attach a small sample CSV when filing the report. Example rows:

Date,transaction_id,amount,description
2026-02-01,TXN12345,100.00,Payment from ACME
2026-02-01,TXN12345,100.00,Payment from ACME

## Screenshots / Attachments
- CSV file with duplicated rows (recommended).
- Ledger screenshot showing duplicate entries (recommended).

## Environment
- OS: Ubuntu 24.04 (server); Client: Windows 10 / macOS (web)
- Browser: Chrome 120+, Firefox 115+
- App Version: 3.4.1
- DB: PostgreSQL 15

## Logs
- Import log example: `INFO: Imported 2 transactions from file; created 2 new records.`
- No exception currently emitted — issue arises from missing deduplication logic.

## Possible Cause
- Import pipeline lacks a deterministic deduplication/normalization step.
- Differences in whitespace, casing, or date formatting prevent matching.

## Proposed Fix
- Compute a canonical transaction key before inserts (normalize reference, trim whitespace, lowercase, normalize date format, round amounts to cents) and skip duplicates.
- Add a database-level safeguard: a unique index on `(account_id, transaction_reference_hash)` or use upsert (`ON CONFLICT`) with a proper conflict target.

## Severity
- **Major** — affects financial correctness and reporting.

## Test Cases
1. Import CSV with a single transaction → ledger shows one entry; balance correct.
2. Import CSV with two identical rows → ledger shows one entry; balance correct.
3. Import CSV with same reference but different whitespace/case → treated as duplicate after normalization.
4. Re-import same file twice → idempotent, no new duplicates.
5. Import with slightly different timestamps but same canonical key → deduplicated.

---

Filed by: QA Team

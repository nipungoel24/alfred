---
type: architecture
layer: database
status: active
tags:
  - database
---

# Transactions

SQLite transaction discipline for a single-process, multi-task backend.

## Model

- One shared connection (`check_same_thread=False`), WAL journal, `busy_timeout=5000`.
- Writes are small and frequent (per-sync-message upserts, per-job status flips); WAL keeps readers unblocked.
- The [[backend.app.db.database.transaction]] context manager is **re-entrancy tolerant**: it begins `IMMEDIATE` only when no transaction is open — callers may already sit inside an implicit transaction from a bare INSERT.

## Commit points that matter

- Sync pages commit the account cursor only after the page completes → resume = refetch page, local dedupe absorbs it ([[All Mail Backfill Flow]]).
- Job status flips commit immediately → worker crashes never orphan work ([[Background Analysis Job Flow]]).
- Batch task derivation saves use one transaction per batch ([[backend.app.db.repositories.Repository.save_tasks_batch]]).
- Migrations run inside `_migrate` with a final commit before index creation ([[Migrations]]).

## Related

- [[Database Overview]]
- [[Database Architecture]]

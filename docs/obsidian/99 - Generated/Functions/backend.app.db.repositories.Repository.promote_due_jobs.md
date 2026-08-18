---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.promote_due_jobs
source: backend/app/db/repositories.py
line: 746
status: active
tags: [database, function]
---

# promote_due_jobs

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Promote retryable_failed jobs whose backoff window has elapsed.

## Location

`backend/app/db/repositories.py:746`

## Signature

```python
(self, now_iso: str | None = None)
```

## Parameters

- `self`
- `now_iso` (`str | None`)

## Calls

- `now` (`datetime.datetime.now`, calls-inferred)

## Called By

- [[backend.tests.test_backfill_jobs.test_backoff_and_promotion_cycle|test_backoff_and_promotion_cycle]]

## Writes

- [[table_jobs]]

## Side Effects

- SQLite

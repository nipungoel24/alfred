---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_backfill_jobs
qualified_name: backend.tests.test_backfill_jobs.test_backoff_and_promotion_cycle
source: backend/tests/test_backfill_jobs.py
line: 103
status: active
tags: [test, function, test]
---

# test_backoff_and_promotion_cycle

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_backoff_and_promotion_cycle` in `backend/tests/test_backfill_jobs.py`.

## Location

`backend/tests/test_backfill_jobs.py:103`

## Signature

```python
(repo)
```

## Parameters

- `repo`

## Calls

- [[backend.app.db.repositories.Repository.enqueue_job|enqueue_job]] (calls)
- [[backend.app.db.repositories.Repository.next_job|next_job]] (calls)
- [[backend.app.db.repositories.Repository.promote_due_jobs|promote_due_jobs]] (calls)
- [[backend.app.db.repositories.Repository.retry_job_with_backoff|retry_job_with_backoff]] (calls)
- [[backend.app.db.repositories.Repository.update_job_status|update_job_status]] (calls)

## Reads

- [[table_jobs]]

## Writes

- [[table_jobs]]

## Side Effects

- SQLite

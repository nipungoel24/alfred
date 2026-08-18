---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_backfill_jobs
qualified_name: backend.tests.test_backfill_jobs.test_requeue_resets_attempts_and_errors
source: backend/tests/test_backfill_jobs.py
line: 90
status: active
tags: [test, function, test]
---

# test_requeue_resets_attempts_and_errors

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_requeue_resets_attempts_and_errors` in `backend/tests/test_backfill_jobs.py`.

## Location

`backend/tests/test_backfill_jobs.py:90`

## Signature

```python
(repo)
```

## Parameters

- `repo`

## Calls

- [[backend.app.db.repositories.Repository.enqueue_job|enqueue_job]] (calls)
- [[backend.app.db.repositories.Repository.job|job]] (calls)
- [[backend.app.db.repositories.Repository.requeue_job|requeue_job]] (calls)
- [[backend.app.db.repositories.Repository.update_job_status|update_job_status]] (calls)

## Reads

- [[table_jobs]]

## Writes

- [[table_jobs]]

## Side Effects

- SQLite

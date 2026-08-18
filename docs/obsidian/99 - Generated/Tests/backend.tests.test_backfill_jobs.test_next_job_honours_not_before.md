---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_backfill_jobs
qualified_name: backend.tests.test_backfill_jobs.test_next_job_honours_not_before
source: backend/tests/test_backfill_jobs.py
line: 84
status: active
tags: [test, function, test]
---

# test_next_job_honours_not_before

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_next_job_honours_not_before` in `backend/tests/test_backfill_jobs.py`.

## Location

`backend/tests/test_backfill_jobs.py:84`

## Signature

```python
(repo)
```

## Parameters

- `repo`

## Calls

- [[backend.app.db.repositories.Repository.enqueue_job|enqueue_job]] (calls)
- [[backend.app.db.repositories.Repository.next_job|next_job]] (calls)

## Reads

- [[table_jobs]]

## Writes

- [[table_jobs]]

## Side Effects

- SQLite

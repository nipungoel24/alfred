---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.requeue_job
source: backend/app/db/repositories.py
line: 650
status: active
tags: [database, function]
---

# requeue_job

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Re-arm a job for its next bounded run (resets attempts/errors).

## Location

`backend/app/db/repositories.py:650`

## Signature

```python
(self, job_id: str, not_before: str | None = None)
```

## Parameters

- `self`
- `job_id` (`str`)
- `not_before` (`str | None`)

## Called By

- [[backend.tests.test_backfill_jobs.test_requeue_resets_attempts_and_errors|test_requeue_resets_attempts_and_errors]]

## Writes

- [[table_jobs]]

## Side Effects

- SQLite

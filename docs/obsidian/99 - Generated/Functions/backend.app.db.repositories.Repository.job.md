---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.job
source: backend/app/db/repositories.py
line: 692
status: active
tags: [database, function]
---

# job

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `job` in `backend/app/db/repositories.py`.

## Location

`backend/app/db/repositories.py:692`

## Signature

```python
(self, job_id: str)
```

## Parameters

- `self`
- `job_id` (`str`)

## Called By

- [[backend.tests.test_backfill_jobs.test_rearm_does_not_touch_backoff_retries|test_rearm_does_not_touch_backoff_retries]]
- [[backend.tests.test_backfill_jobs.test_rearm_terminal_job_for_resume|test_rearm_terminal_job_for_resume]]
- [[backend.tests.test_backfill_jobs.test_requeue_resets_attempts_and_errors|test_requeue_resets_attempts_and_errors]]

## Reads

- [[table_jobs]]

## Side Effects

- SQLite

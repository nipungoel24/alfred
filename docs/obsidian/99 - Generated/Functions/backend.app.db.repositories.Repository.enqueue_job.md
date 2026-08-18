---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.enqueue_job
source: backend/app/db/repositories.py
line: 615
status: active
tags: [database, function]
---

# enqueue_job

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Enqueue a background job. Idempotent — skips if job already exists.

## Location

`backend/app/db/repositories.py:615`

## Signature

```python
(self, job_id: str, job_type: str, target_id: str, priority: int = 50, not_before: str | None = None)
```

## Parameters

- `self`
- `job_id` (`str`)
- `job_type` (`str`)
- `target_id` (`str`)
- `priority` (`int`)
- `not_before` (`str | None`)

## Calls

- `now` (`datetime.datetime.now`, calls-inferred)

## Called By

- [[backend.tests.test_backfill_jobs.test_backfill_job_is_single_durable_row|test_backfill_job_is_single_durable_row]]
- [[backend.tests.test_backfill_jobs.test_backfill_priority_is_below_analysis|test_backfill_priority_is_below_analysis]]
- [[backend.tests.test_backfill_jobs.test_backoff_and_promotion_cycle|test_backoff_and_promotion_cycle]]
- [[backend.tests.test_backfill_jobs.test_next_job_honours_not_before|test_next_job_honours_not_before]]
- [[backend.tests.test_backfill_jobs.test_rearm_does_not_touch_backoff_retries|test_rearm_does_not_touch_backoff_retries]]
- [[backend.tests.test_backfill_jobs.test_rearm_terminal_job_for_resume|test_rearm_terminal_job_for_resume]]
- [[backend.tests.test_backfill_jobs.test_requeue_resets_attempts_and_errors|test_requeue_resets_attempts_and_errors]]

## Writes

- [[table_jobs]]

## Side Effects

- SQLite

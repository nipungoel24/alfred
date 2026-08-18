---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.update_job_status
source: backend/app/db/repositories.py
line: 696
status: active
tags: [database, function]
---

# update_job_status

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `update_job_status` in `backend/app/db/repositories.py`.

## Location

`backend/app/db/repositories.py:696`

## Signature

```python
(self, job_id: str, status: str, error_code: str = None, error_message: str = None)
```

## Parameters

- `self`
- `job_id` (`str`)
- `status` (`str`)
- `error_code` (`str`)
- `error_message` (`str`)

## Calls

- `now` (`datetime.datetime.now`, calls-inferred)

## Called By

- [[backend.tests.test_backfill_jobs.test_backoff_and_promotion_cycle|test_backoff_and_promotion_cycle]]
- [[backend.tests.test_backfill_jobs.test_rearm_does_not_touch_backoff_retries|test_rearm_does_not_touch_backoff_retries]]
- [[backend.tests.test_backfill_jobs.test_rearm_terminal_job_for_resume|test_rearm_terminal_job_for_resume]]
- [[backend.tests.test_backfill_jobs.test_requeue_resets_attempts_and_errors|test_requeue_resets_attempts_and_errors]]

## Writes

- [[table_jobs]]

## Side Effects

- SQLite

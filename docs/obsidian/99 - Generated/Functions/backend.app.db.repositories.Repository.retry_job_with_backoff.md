---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.retry_job_with_backoff
source: backend/app/db/repositories.py
line: 681
status: active
tags: [database, function]
---

# retry_job_with_backoff

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Mark a job retryable_failed with a not_before backoff timestamp.

## Location

`backend/app/db/repositories.py:681`

## Signature

```python
(self, job_id: str, error_code: str, error_message: str, not_before: str)
```

## Parameters

- `self`
- `job_id` (`str`)
- `error_code` (`str`)
- `error_message` (`str`)
- `not_before` (`str`)

## Calls

- `now` (`datetime.datetime.now`, calls-inferred)

## Called By

- [[backend.tests.test_backfill_jobs.test_backoff_and_promotion_cycle|test_backoff_and_promotion_cycle]]
- [[backend.tests.test_backfill_jobs.test_rearm_does_not_touch_backoff_retries|test_rearm_does_not_touch_backoff_retries]]

## Writes

- [[table_jobs]]

## Side Effects

- SQLite

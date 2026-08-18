---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.tests.test_backfill_jobs
source: backend/tests/test_backfill_jobs.py
status: active
tags: [module, backend]
---

# backend.tests.test_backfill_jobs

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/tests/test_backfill_jobs.py`

## Imports

- `BackfillState` ← `backend.app.mail.eligibility.BackfillState`
- `Repository` ← `backend.app.db.repositories.Repository`
- `datetime` ← `datetime.datetime`
- `json` ← `json`
- `normalize_cursor` ← `backend.app.mail.backfill.normalize_cursor`
- `pytest` ← `pytest`
- `set_state` ← `backend.app.mail.backfill.set_state`
- `status_payload` ← `backend.app.mail.backfill.status_payload`
- `timedelta` ← `datetime.timedelta`
- `timezone` ← `datetime.timezone`

## Functions

- [[backend.tests.test_backfill_jobs._future|_future]]
- [[backend.tests.test_backfill_jobs._past|_past]]
- [[backend.tests.test_backfill_jobs.repo|repo]]

## Tests

- [[backend.tests.test_backfill_jobs.test_backfill_job_is_single_durable_row|test_backfill_job_is_single_durable_row]]
- [[backend.tests.test_backfill_jobs.test_backfill_priority_is_below_analysis|test_backfill_priority_is_below_analysis]]
- [[backend.tests.test_backfill_jobs.test_backoff_and_promotion_cycle|test_backoff_and_promotion_cycle]]
- [[backend.tests.test_backfill_jobs.test_next_job_honours_not_before|test_next_job_honours_not_before]]
- [[backend.tests.test_backfill_jobs.test_normalize_fresh_cursor|test_normalize_fresh_cursor]]
- [[backend.tests.test_backfill_jobs.test_normalize_legacy_complete_cursor|test_normalize_legacy_complete_cursor]]
- [[backend.tests.test_backfill_jobs.test_normalize_legacy_running_cursor|test_normalize_legacy_running_cursor]]
- [[backend.tests.test_backfill_jobs.test_rearm_does_not_touch_backoff_retries|test_rearm_does_not_touch_backoff_retries]]
- [[backend.tests.test_backfill_jobs.test_rearm_terminal_job_for_resume|test_rearm_terminal_job_for_resume]]
- [[backend.tests.test_backfill_jobs.test_requeue_resets_attempts_and_errors|test_requeue_resets_attempts_and_errors]]
- [[backend.tests.test_backfill_jobs.test_status_payload_complete|test_status_payload_complete]]
- [[backend.tests.test_backfill_jobs.test_status_payload_remaining_estimate|test_status_payload_remaining_estimate]]

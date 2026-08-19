---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.backfill
qualified_name: backend.app.mail.backfill.normalize_cursor
source: backend/app/mail/backfill.py
line: 35
status: active
tags: [gmail, function]
---

# normalize_cursor

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Parse a sync cursor and normalize its backfill block.

## Location

`backend/app/mail/backfill.py:35`

## Signature

```python
(sync_cursor: str | None) -> dict
```

## Parameters

- `sync_cursor` (`str | None`)

## Returns

`dict`

## Calls

- `loads` (`json.loads`, calls-inferred)

## Called By

- [[backend.app.main._backfill_estimate_once|_backfill_estimate_once]]
- [[backend.app.main._backfill_worker|_backfill_worker]]
- [[backend.app.main._mark_backfill_failure|_mark_backfill_failure]]
- [[backend.app.main._set_backfill_state|_set_backfill_state]]
- [[backend.app.main._startup_background|_startup_background]]
- [[backend.app.main.backfill_account|backfill_account]]
- [[backend.app.main.backfill_status|backfill_status]]
- [[backend.app.main.get_accounts|get_accounts]]
- [[backend.app.main.pause_backfill|pause_backfill]]
- [[backend.app.main.sync_account|sync_account]]
- [[backend.tests.test_backfill_jobs.test_normalize_fresh_cursor|test_normalize_fresh_cursor]]
- [[backend.tests.test_backfill_jobs.test_normalize_legacy_complete_cursor|test_normalize_legacy_complete_cursor]]
- [[backend.tests.test_backfill_jobs.test_normalize_legacy_running_cursor|test_normalize_legacy_running_cursor]]
- [[backend.tests.test_backfill_jobs.test_status_payload_complete|test_status_payload_complete]]
- [[backend.tests.test_backfill_jobs.test_status_payload_remaining_estimate|test_status_payload_remaining_estimate]]

## Side Effects

- none statically observed

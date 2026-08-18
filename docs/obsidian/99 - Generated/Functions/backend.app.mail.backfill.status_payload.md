---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.backfill
qualified_name: backend.app.mail.backfill.status_payload
source: backend/app/mail/backfill.py
line: 93
status: active
tags: [gmail, function]
---

# status_payload

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Observer-facing backfill status (no tokens, no secrets).

## Location

`backend/app/mail/backfill.py:93`

## Signature

```python
(data: dict) -> dict
```

## Parameters

- `data` (`dict`)

## Returns

`dict`

## Called By

- [[backend.app.main.backfill_account|backfill_account]]
- [[backend.app.main.backfill_status|backfill_status]]
- [[backend.app.main.get_accounts|get_accounts]]
- [[backend.app.main.pause_backfill|pause_backfill]]
- [[backend.tests.test_backfill_jobs.test_status_payload_complete|test_status_payload_complete]]
- [[backend.tests.test_backfill_jobs.test_status_payload_remaining_estimate|test_status_payload_remaining_estimate]]

## Side Effects

- none statically observed

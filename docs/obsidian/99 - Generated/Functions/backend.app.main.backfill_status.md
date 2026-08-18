---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main.backfill_status
source: backend/app/main.py
line: 710
status: active
tags: [backend, function, endpoint]
---

# backfill_status

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Observer-facing backfill status (typed state, counters, estimate).

## Route

`GET /api/accounts/{account_id}/backfill`

## Location

`backend/app/main.py:710`

## Signature

```python
(account_id: str)
```

## Parameters

- `account_id` (`str`)

## Calls

- [[backend.app.mail.backfill.normalize_cursor|normalize_cursor]] (calls)
- [[backend.app.mail.backfill.status_payload|status_payload]] (calls)
- `HTTPException` (`fastapi.HTTPException`, calls-inferred)

## Side Effects

- none statically observed

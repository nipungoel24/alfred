---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main.backfill_account
source: backend/app/main.py
line: 727
status: active
tags: [backend, function, endpoint]
---

# backfill_account

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Start/resume the durable All Mail backfill (backend-owned).

## Route

`POST /api/accounts/{account_id}/backfill`

## Location

`backend/app/main.py:727`

## Signature

```python
(account_id: str)
```

## Parameters

- `account_id` (`str`)

## Calls

- [[backend.app.mail.backfill.dump_cursor|dump_cursor]] (calls)
- [[backend.app.mail.backfill.normalize_cursor|normalize_cursor]] (calls)
- [[backend.app.mail.backfill.set_state|set_state]] (calls)
- [[backend.app.mail.backfill.status_payload|status_payload]] (calls)
- `HTTPException` (`fastapi.HTTPException`, calls-inferred)

## Side Effects

- async I/O

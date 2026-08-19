---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main.pause_backfill
source: backend/app/main.py
line: 733
status: active
tags: [backend, function, endpoint]
---

# pause_backfill

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Pause the durable backfill. Progress and cursor are preserved.

## Route

`POST /api/accounts/{account_id}/backfill/pause`

## Location

`backend/app/main.py:733`

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

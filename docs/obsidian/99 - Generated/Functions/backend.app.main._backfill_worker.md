---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main._backfill_worker
source: backend/app/main.py
line: 74
status: active
tags: [backend, function, critical-path]
---

# _backfill_worker

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Durable worker for the progressive All Mail backfill.

## Location

`backend/app/main.py:74`

## Signature

```python
()
```

## Calls

- `sleep` (`asyncio.sleep`, calls-inferred)
- [[backend.app.db.secure_store.decrypt_token|decrypt_token]] (calls)
- [[backend.app.mail.backfill.normalize_cursor|normalize_cursor]] (calls)
- `now` (`datetime.datetime.now`, calls-inferred)
- `timedelta` (`datetime.timedelta`, calls-inferred)

## Side Effects

- async I/O

---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main._backfill_estimate_once
source: backend/app/main.py
line: 358
status: active
tags: [backend, function]
---

# _backfill_estimate_once

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

One-shot resultSizeEstimate for accounts whose backfill is already

## Location

`backend/app/main.py:358`

## Signature

```python
()
```

## Calls

- [[backend.app.db.secure_store.decrypt_token|decrypt_token]] (calls)
- [[backend.app.mail.backfill.dump_cursor|dump_cursor]] (calls)
- [[backend.app.mail.backfill.normalize_cursor|normalize_cursor]] (calls)

## Side Effects

- async I/O

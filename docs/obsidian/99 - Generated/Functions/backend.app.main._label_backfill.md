---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main._label_backfill
source: backend/app/main.py
line: 359
status: active
tags: [backend, function]
---

# _label_backfill

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Refresh Gmail labels for cached rows missing mailbox state.

## Location

`backend/app/main.py:359`

## Signature

```python
()
```

## Calls

- [[backend.app.db.secure_store.decrypt_token|decrypt_token]] (calls)
- [[backend.app.mail.identity.provider_message_id|provider_message_id]] (calls)
- [[backend.app.mail.identity.strip_scope|strip_scope]] (calls)

## Side Effects

- async I/O

---
type: function
generated: true
language: python
layer: database
module: backend.app.db.secure_store
qualified_name: backend.app.db.secure_store.decrypt_token
source: backend/app/db/secure_store.py
line: 46
status: active
tags: [database, function]
---

# decrypt_token

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `decrypt_token` in `backend/app/db/secure_store.py`.

## Location

`backend/app/db/secure_store.py:46`

## Signature

```python
(enc_data: bytes) -> str
```

## Parameters

- `enc_data` (`bytes`)

## Returns

`str`

## Calls

- `b64decode` (`base64.b64decode`, calls-inferred)

## Called By

- [[backend.app.main._backfill_estimate_once|_backfill_estimate_once]]
- [[backend.app.main._backfill_worker|_backfill_worker]]
- [[backend.app.main._label_backfill|_label_backfill]]
- [[backend.app.main.sync_account|sync_account]]

## Side Effects

- handles credentials/tokens — see [[Token Security]]

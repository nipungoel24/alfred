---
type: function
generated: true
language: python
layer: database
module: backend.app.db.secure_store
qualified_name: backend.app.db.secure_store._win_decrypt
source: backend/app/db/secure_store.py
line: 19
status: active
tags: [database, function]
---

# _win_decrypt

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `_win_decrypt` in `backend/app/db/secure_store.py`.

## Location

`backend/app/db/secure_store.py:19`

## Signature

```python
(enc_data: bytes) -> bytes
```

## Parameters

- `enc_data` (`bytes`)

## Returns

`bytes`

## Side Effects

- handles credentials/tokens — see [[Token Security]]

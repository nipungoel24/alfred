---
type: function
generated: true
language: python
layer: database
module: backend.app.db.secure_store
qualified_name: backend.app.db.secure_store.encrypt_token
source: backend/app/db/secure_store.py
line: 34
status: active
tags: [database, function]
---

# encrypt_token

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `encrypt_token` in `backend/app/db/secure_store.py`.

## Location

`backend/app/db/secure_store.py:34`

## Signature

```python
(token: str) -> bytes
```

## Parameters

- `token` (`str`)

## Returns

`bytes`

## Calls

- `b64encode` (`base64.b64encode`, calls-inferred)

## Called By

- [[backend.app.main.gmail_callback|gmail_callback]]

## Side Effects

- handles credentials/tokens — see [[Token Security]]

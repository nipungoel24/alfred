---
type: function
generated: true
language: python
layer: database
module: backend.app.db.secure_store
qualified_name: backend.app.db.secure_store._looks_like_dpapi
source: backend/app/db/secure_store.py
line: 157
status: active
tags: [database, function]
---

# _looks_like_dpapi

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

A DPAPI blob always begins with a versioned header byte.

## Location

`backend/app/db/secure_store.py:157`

## Signature

```python
(blob: bytes) -> bool
```

## Parameters

- `blob` (`bytes`)

## Returns

`bool`

## Side Effects

- handles credentials/tokens — see [[Token Security]]

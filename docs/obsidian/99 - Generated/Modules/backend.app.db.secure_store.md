---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.app.db.secure_store
source: backend/app/db/secure_store.py
status: active
tags: [module, backend]
---

# backend.app.db.secure_store

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/app/db/secure_store.py`

## Imports

- `annotations` ← `__future__.annotations`
- `base64` ← `base64`
- `binascii` ← `binascii`
- `logging` ← `logging`
- `sys` ← `sys`

## Classes

- [[backend.app.db.secure_store.SecureStoreUnavailable|SecureStoreUnavailable]]

## Functions

- [[backend.app.db.secure_store._looks_like_dpapi|_looks_like_dpapi]]
- [[backend.app.db.secure_store._win_decrypt|_win_decrypt]]
- [[backend.app.db.secure_store._win_encrypt|_win_encrypt]]
- [[backend.app.db.secure_store.decrypt_token|decrypt_token]]
- [[backend.app.db.secure_store.encrypt_token|encrypt_token]]
- [[backend.app.db.secure_store.is_available|is_available]]
- [[backend.app.db.secure_store.status|status]]

## Constants

- `FORMAT_VERSION`
- `_FORCE_UNAVAILABLE`

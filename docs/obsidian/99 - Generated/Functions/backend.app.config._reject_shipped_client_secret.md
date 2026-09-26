---
type: function
generated: true
language: python
layer: backend
module: backend.app.config
qualified_name: backend.app.config._reject_shipped_client_secret
source: backend/app/config.py
line: 61
status: active
tags: [backend, function]
---

# _reject_shipped_client_secret

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

A frozen Alfred must not be carrying a Google OAuth client secret.

## Location

`backend/app/config.py:61`

## Signature

```python
() -> None
```

## Returns

`None`

## Calls

- `getenv` (`os.getenv`, calls-inferred)

## Side Effects

- none statically observed

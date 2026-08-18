---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main.generate_pkce_pair
source: backend/app/main.py
line: 319
status: active
tags: [backend, function]
---

# generate_pkce_pair

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `generate_pkce_pair` in `backend/app/main.py`.

## Location

`backend/app/main.py:319`

## Signature

```python
()
```

## Calls

- `urlsafe_b64encode` (`base64.urlsafe_b64encode`, calls-inferred)
- `sha256` (`hashlib.sha256`, calls-inferred)
- `token_urlsafe` (`secrets.token_urlsafe`, calls-inferred)

## Side Effects

- none statically observed

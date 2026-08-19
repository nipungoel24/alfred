---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main.generate_briefing
source: backend/app/main.py
line: 951
status: active
tags: [backend, function, endpoint]
---

# generate_briefing

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `generate_briefing` in `backend/app/main.py`.

## Route

`POST /api/briefing/generate`

## Location

`backend/app/main.py:951`

## Signature

```python
(force: bool = True)
```

## Parameters

- `force` (`bool`)

## Calls

- [[backend.app.mail.briefing_fingerprint.briefing_fingerprint|briefing_fingerprint]] (calls)

## Side Effects

- async I/O

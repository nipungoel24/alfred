---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main.analysis_retry
source: backend/app/main.py
line: 926
status: active
tags: [backend, function, endpoint]
---

# analysis_retry

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Manual recovery trigger: reset backoff and re-check AI health now.

## Route

`POST /api/analysis/retry`

## Location

`backend/app/main.py:926`

## Signature

```python
()
```

## Side Effects

- async I/O

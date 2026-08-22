---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main._analysis_worker
source: backend/app/main.py
line: 191
status: active
tags: [backend, function, critical-path]
---

# _analysis_worker

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Background worker that processes analysis jobs from SQLite.

## Location

`backend/app/main.py:191`

## Signature

```python
()
```

## Calls

- `sleep` (`asyncio.sleep`, calls-inferred)
- [[backend.app.mail.fingerprint.content_fingerprint|content_fingerprint]] (calls)

## Side Effects

- async I/O

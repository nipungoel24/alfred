---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main.analysis_progress
source: backend/app/main.py
line: 778
status: active
tags: [backend, function, endpoint]
---

# analysis_progress

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Server-Sent Events endpoint for real-time analysis progress.

## Route

`GET /api/analysis/progress`

## Location

`backend/app/main.py:778`

## Signature

```python
()
```

## Calls

- `Queue` (`asyncio.Queue`, calls-inferred)
- `wait_for` (`asyncio.wait_for`, calls-inferred)
- `StreamingResponse` (`fastapi.responses.StreamingResponse`, calls-inferred)
- `dumps` (`json.dumps`, calls-inferred)

## Side Effects

- async I/O

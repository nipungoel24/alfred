---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.supervisor.AISupervisor
qualified_name: backend.app.ai.supervisor.AISupervisor._try_auto_start
source: backend/app/ai/supervisor.py
line: 455
status: active
tags: [ai, function]
---

# _try_auto_start

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Start the Ollama server once if installed and not running.

## Location

`backend/app/ai/supervisor.py:455`

## Signature

```python
(self)
```

## Parameters

- `self`

## Calls

- `sleep` (`asyncio.sleep`, calls-inferred)
- `Popen` (`subprocess.Popen`, calls-inferred)

## Side Effects

- async I/O

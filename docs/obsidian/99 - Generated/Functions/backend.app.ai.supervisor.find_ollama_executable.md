---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.supervisor
qualified_name: backend.app.ai.supervisor.find_ollama_executable
source: backend/app/ai/supervisor.py
line: 69
status: active
tags: [ai, function]
---

# find_ollama_executable

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Locate the Ollama executable on this machine, or None.

## Location

`backend/app/ai/supervisor.py:69`

## Signature

```python
() -> str | None
```

## Returns

`str | None`

## Calls

- `get` (`os.environ.get`, calls-inferred)
- `isfile` (`os.path.isfile`, calls-inferred)
- `join` (`os.path.join`, calls-inferred)
- `which` (`shutil.which`, calls-inferred)

## Side Effects

- none statically observed

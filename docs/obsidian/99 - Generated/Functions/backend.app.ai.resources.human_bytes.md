---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.resources
qualified_name: backend.app.ai.resources.human_bytes
source: backend/app/ai/resources.py
line: 190
status: active
tags: [ai, function]
---

# human_bytes

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Format bytes with binary units, consistently across every surface.

## Location

`backend/app/ai/resources.py:190`

## Signature

```python
(value: int | None) -> str
```

## Parameters

- `value` (`int | None`)

## Returns

`str`

## Called By

- [[backend.app.ai.supervisor.AISupervisor._run_pull|_run_pull]]
- [[backend.app.ai.supervisor.AISupervisor.pull_payload|pull_payload]]
- [[backend.app.main.ai_model|ai_model]]
- [[backend.tests.test_model_pull.test_human_bytes_formats_consistently|test_human_bytes_formats_consistently]]

## Side Effects

- none statically observed

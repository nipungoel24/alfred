---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main._derive_and_save_tasks
source: backend/app/main.py
line: 300
status: active
tags: [backend, function]
---

# _derive_and_save_tasks

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Derive tasks from analysis and persist them, deduplicating.

## Location

`backend/app/main.py:300`

## Signature

```python
(email: Email, analysis: EmailAnalysis)
```

## Parameters

- `email` (`Email`)
- `analysis` (`EmailAnalysis`)

## Calls

- [[backend.app.services.task_derivation.derive_tasks|derive_tasks]] (calls)

## Side Effects

- none statically observed

---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.record_inference_metric
source: backend/app/db/repositories.py
line: 760
status: active
tags: [database, function]
---

# record_inference_metric

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `record_inference_metric` in `backend/app/db/repositories.py`.

## Location

`backend/app/db/repositories.py:760`

## Signature

```python
(self, job_id: str, model: str, total_ms: float = 0, load_ms: float = 0, prompt_eval_ms: float = 0, eval_ms: float = 0, prompt_tokens: int = 0, output_tokens: int = 0, cache_hit: bool = False, success: bool = True)
```

## Parameters

- `self`
- `job_id` (`str`)
- `model` (`str`)
- `total_ms` (`float`)
- `load_ms` (`float`)
- `prompt_eval_ms` (`float`)
- `eval_ms` (`float`)
- `prompt_tokens` (`int`)
- `output_tokens` (`int`)
- `cache_hit` (`bool`)
- `success` (`bool`)

## Calls

- `now` (`datetime.datetime.now`, calls-inferred)

## Writes

- [[table_inference_metrics]]

## Side Effects

- SQLite

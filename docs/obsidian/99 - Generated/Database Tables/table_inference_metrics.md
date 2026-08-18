---
type: database-table
generated: true
layer: database
qualified_name: table_inference_metrics
source: backend/app/db/database.py
status: active
tags: [database, database-table]
---

# inference_metrics

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

SQLite table `inference_metrics` defined in the Alfred schema.

## Columns

- `id` · PRIMARY KEY
- `job_id`
- `model`
- `total_ms`
- `load_ms`
- `prompt_eval_ms`
- `eval_ms`
- `prompt_tokens`
- `output_tokens`
- `cache_hit`
- `success`
- `recorded_at`

## Ownership

See [[Data Ownership]] for source/derived/user-state classification.

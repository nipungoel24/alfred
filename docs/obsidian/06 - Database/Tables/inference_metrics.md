---
type: database-table
layer: database
status: active
source: backend/app/db/database.py
tags:
  - database
---

# inference_metrics

Per-inference telemetry for the local model — the data behind [[AI Performance]].

## Data classification

**Telemetry.** One row per successful analysis job (plus failures where recorded): `job_id` → [[jobs]], model, total/load/prompt-eval/eval timings (ms), token counts, cache-hit flag, success flag.

## Written By

- [[backend.app.main._analysis_worker]] via [[backend.app.db.repositories.Repository.record_inference_metric]]

## Read By

- Nothing in the product UI yet; consumed by benchmarks (`backend/benchmarks/`) and [[Performance Benchmarks]].

Schema detail: [[table_inference_metrics]].

## Related

- [[AI Performance]]
- [[jobs]]

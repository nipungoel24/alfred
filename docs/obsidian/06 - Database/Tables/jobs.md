---
type: database-table
layer: database
status: active
source: backend/app/db/database.py
tags:
  - database
---

# jobs

The durable queue behind every background loop. This table is Alfred's "process memory" — nothing in RAM is ever the queue.

## Data classification

**Process state** — durable by design; a restart mid-anything loses nothing.

## Columns that matter

- `id` — deterministic ids (`analyze_<email_id>`, `backfill_gmail_<account_id>`) make enqueue idempotent.
- `job_type` — `analyze_email` | `backfill_gmail`.
- `priority` — higher first (analysis 100→10; backfill 5, always below analysis).
- `status` — `queued → running → succeeded | retryable_failed → queued | failed | cancelled | paused`.
- `attempts` / `max_attempts` — retry budget.
- `not_before` — scheduled re-arm + exponential backoff ([[backend.app.db.repositories.Repository.next_job]] ignores future rows).

Schema detail: [[table_jobs]].

## Written By

- [[POST --api-accounts-{account_id}-sync|sync_account]] (analysis enqueue)
- [[POST --api-emails-analyze]], [[POST --api-emails-{email_id}-analyze]]
- [[backend.app.main._backfill_worker]] (requeue/backoff)
- [[backend.app.main.lifespan]] (startup healing)

## Read By

- [[backend.app.main._analysis_worker]]
- [[backend.app.main._backfill_worker]]
- [[GET --api-analysis-status]]

## Related

- [[Background Analysis Job Flow]]
- [[All Mail Backfill Flow]]
- [[inference_metrics]]

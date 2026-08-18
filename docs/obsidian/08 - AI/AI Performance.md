---
type: architecture
layer: ai
status: active
tags:
  - ai
---

# AI Performance

Measured behavior of the local inference path, and the levers that keep it fast.

## Measurement

Every successful analysis records ms-level timings + token counts in [[inference_metrics]] ([[backend.app.db.repositories.Repository.record_inference_metric]]); `backend/benchmarks/` contains the harness and `docs/engineering/performance-*.md` holds the historical baselines ([[Performance Benchmarks]]).

## The levers actually used

1. **Model preload at startup** — kills first-inference cold start.
2. **Body truncation (2000 chars)** — prompt stays ≈1.2K tokens of a 32K context; faster prompt-eval.
3. **`think: false` + `stream: false`** — no reasoning tokens, single response.
4. **Eligibility-driven scheduling** — promotions/social deferred; the queue processes what matters first ([[backend.app.mail.eligibility.MailEligibilityPolicy.analysis_queue_priority|analysis_queue_priority]]).
5. **Durable cache hits** — unchanged mail never re-inferred ([[AI Caching]]).
6. **Persistent jobs with backoff** — no hot retry loops during outages ([[AI Failure Handling]]).

## Known costs

- Analysis is CPU/GPU-bound on the host; the worker is single-concurrency by design (`WORKER_CONCURRENCY = 1`) so the UI machine never thrashes.
- Backfill pages are rate-limited (`not_before +2.5s`) and run at priority 5 — always below analysis ([[All Mail Backfill Flow]]).

## Related

- [[Ollama Integration]]
- [[Model Configuration]]
- [[inference_metrics]]

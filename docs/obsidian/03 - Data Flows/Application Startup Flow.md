---
type: data-flow
layer: backend
status: active
tags:
  - system
  - backend
  - critical-path
---

# Application Startup Flow

What happens in the first seconds of the backend — ordered, idempotent, crash-safe.

1. **Database** — [[backend.app.db.database.connect]]: PRAGMAs (WAL, foreign keys, busy timeout), schema creation, additive migrations + in-place backfills (labels/state/eligibility, payload repair), indexes, FTS5.
2. **Model preload** — [[backend.app.ai.ollama_client.OllamaClient.preload_model]]; failure is non-fatal.
3. **Task reconciliation** — [[backend.app.services.task_derivation.rebuild_tasks_from_analyses|rebuild_tasks_from_analyses]] if the derivation version moved (no LLM calls).
4. **Queue healing** — stuck `running` jobs → `queued`; retryable jobs reset ([[Background Analysis Job Flow]]).
5. **Backfill resume** — for every connected Gmail account whose typed `backfill_state` is `not_started`/`running`, arm the durable job ([[All Mail Backfill Flow]]).
6. **Workers** — analysis worker + backfill worker start polling [[jobs]].
7. **One-shot housekeeping** — label backfill for legacy rows (METADATA-only), and a one-time `resultSizeEstimate` fetch for legacy-complete backfills.
8. **Serve** — uvicorn binds `127.0.0.1:8765`.

Every step is exception-guarded; a failure in one never prevents the API from serving.

## Frontend startup

`index.html` applies the resolved theme before first paint (no flash); React mounts providers ([[frontend.src.theme.ThemeProvider.ThemeProvider|ThemeProvider]] → QueryClient) and [[frontend.src.App.App]] lands on the Mail workspace.

## Related

- [[Application Shutdown Flow]]
- [[Runtime Lifecycle]]
- [[Entry Points]]

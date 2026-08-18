---
type: data-flow
layer: backend
status: active
tags:
  - system
  - backend
---

# Application Shutdown Flow

Graceful teardown in [[backend.app.main.lifespan]]:

1. Flip `_worker_running` / `_backfill_running` to false — workers stop picking new jobs after the current iteration.
2. Cancel both worker tasks and the one-shot tasks (label backfill, estimate fetch); swallow `CancelledError`.
3. `repo.close()` — SQLite connection closed (WAL checkpointed by SQLite).

## Why this is enough

- No in-memory queue to drain: every unit of work is a row in [[jobs]] or a cursor field in [[accounts]].
- An in-flight Ollama call may be abandoned mid-request — the corresponding job row is still `running` and gets reset to `queued` at the next startup ([[Application Startup Flow]]).
- A backfill page is committed (counters + page token) *after* the page completes, so a kill mid-page simply re-fetches that page later; the local cache dedupes by message id.

## Desktop

Tauri keeps the sidecar child handle managed, so app exit kills the backend process; the same guarantees apply. See [[Windows Lifecycle]].

## Related

- [[Application Startup Flow]]
- [[Runtime Lifecycle]]
- [[All Mail Backfill Flow]]

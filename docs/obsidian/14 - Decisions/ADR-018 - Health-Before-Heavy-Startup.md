---
type: adr
layer: meta
status: active
tags:
  - architecture
  - desktop
  - critical-path
---

# ADR-018 - Health-Before-Heavy-Startup

## Status

Accepted

## Context

Release-candidate field testing produced a repeated installed-startup failure ("Alfred couldn't start its local service"). Diagnosis showed a three-part defect:

1. The backend lifespan `await ai.preload()` **before** yielding — while Ollama loaded qwen3:4b, uvicorn held every request, so `/health` hung and the desktop shell's bounded readiness probe reported failure.
2. The frontend resolved the runtime endpoint (`backend_info`) exactly once; if the webview loaded before the shell finished spawning, it silently fell back to dev defaults **permanently** — every Retry respawned the backend but the client never re-initialized, producing a failure loop.
3. `retry_backend` killed a healthy-but-late backend and restarted the slow cold-start cycle; the UI gate budget (~15s) was far shorter than the shell budget (45s).

## Decision

- `/health` must serve immediately after socket bind: all slow startup work (model preload, task rebuild, queue healing, backfill resume) runs in background tasks **after** the lifespan yields.
- Frontend endpoint resolution retries for a bounded window; Retry re-resolves the endpoint before re-polling.
- `retry_backend` probes the current backend first — if healthy, it only re-reveals; it respawns only when the child is dead.
- The frontend gate budget is aligned to the shell budget (45s) with a diagnostic code and a log-path affordance in the failure UI.
- Safe startup logs: `desktop.log` (shell) and `backend.log` (sidecar) under `%LOCALAPPDATA%\AlfredData\logs` — statuses/ports/PIDs only, never secrets.

## Consequences

- Cold starts answer health in ~3s regardless of Ollama/model state.
- Startup failures are diagnosable from logs without reproducing in a debugger.
- Regression tests pin the health-during-lifespan behavior and the gate timing.

## Related Code

- `_startup_background` in [[backend.app.main]]
- `desktop/src-tauri/src/main.rs` (probe logging, retry semantics)
- [[frontend.src.layout.StartupGate.StartupGate|StartupGate]], [[frontend.src.api.client.initApi|initApi]]

## Related Documentation

- [[Windows Lifecycle]]
- [[Debugging]]
- [[backend.tests.test_desktop_startup]]

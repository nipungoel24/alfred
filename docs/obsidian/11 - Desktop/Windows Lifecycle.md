---
type: architecture
layer: desktop
status: active
tags:
  - desktop
---

# Windows Lifecycle

The desktop process tree over time.

1. User launches Alfred → Tauri main process; single-instance plugin makes any second launch focus the first window and exit.
2. `setup` picks a free loopback port + generates the runtime token, spawns the sidecar ([[Sidecar Architecture]]), and polls `/health` for ≤45s.
3. Ready → window shows; frontend bootstrap (`backend_info`) points the API client at the dynamic port with the token.
4. Backend runs its own lifecycle inside the child ([[Application Startup Flow]]).
5. Close → `ExitRequested` handler POSTs `/api/shutdown` (graceful worker stop + SQLite close), then kills the child; Tauri exits. No orphan processes, port released.
6. Force-kill of the backend leaves the app window alive; relaunching the app restarts the sidecar and startup healing requeues any stale `running` jobs ([[Application Shutdown Flow]]).

## Related

- [[Tauri Overview]]
- [[Desktop Architecture]]
- [[ADR-016 - Tauri-Owned Sidecar Lifecycle]]

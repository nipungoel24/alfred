---
type: architecture
layer: desktop
status: active
tags:
  - desktop
---

# Windows Lifecycle

The desktop process tree over time.

1. User launches the Alfred executable → Tauri main process starts.
2. `setup` spawns the sidecar ([[Sidecar Architecture]]) and creates the window (dev URL or bundled dist).
3. Webview loads the frontend; pre-paint theme script applies; queries hit `127.0.0.1:8765`.
4. Backend runs its own lifecycle inside the child process ([[Application Startup Flow]]).
5. On window close/app quit → Tauri kills the managed sidecar child; SQLite closes through the backend's lifespan ([[Application Shutdown Flow]]).

Crash cases: if the sidecar dies unexpectedly, Tauri does not auto-restart it in the current implementation — the webview surfaces connection errors and the app can be relaunched.

## Related

- [[Tauri Overview]]
- [[Runtime Lifecycle]]

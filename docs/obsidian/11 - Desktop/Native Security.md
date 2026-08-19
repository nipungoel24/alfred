---
type: architecture
layer: desktop
status: active
tags:
  - desktop
  - security
---

# Native Security

The desktop-specific parts of the trust boundary, as implemented in v0.1.0.

- **CSP** — `default-src 'self'; connect-src 'self' http://127.0.0.1:* http://localhost:5173 ipc: http://ipc.localhost; img-src 'self' data:; font-src 'self' data:; style-src 'self' 'unsafe-inline'` — the webview can only reach loopback (any port, since the backend port is dynamic) and the dev origin.
- **Capabilities** — `core:default` ONLY. No shell, no filesystem, no process-spawn permissions for the webview. Sidecar spawning happens in Rust; React cannot spawn processes ([[ADR-016 - Tauri-Owned Sidecar Lifecycle]]).
- **Session auth** — per-launch token + dynamic port ([[ADR-015 - Desktop Session Authentication]]).
- **Sidecar process** — loopback bind, DPAPI token storage, SQLite in user AppData ([[DPAPI]], [[Local API Security]]).

## Related

- [[Threat Model]]
- [[Tauri Overview]]
- [[Security Architecture]]

---
type: architecture
layer: desktop
status: active
tags:
  - desktop
  - security
---

# Native Security

The desktop-specific parts of the trust boundary.

- **CSP** — `default-src 'self'; connect-src 'self' http://127.0.0.1:8765 http://localhost:5173; style-src 'self' 'unsafe-inline'` — the webview can only talk to the local backend, never arbitrary hosts.
- **Capabilities** — exactly `core:default` + `shell:allow-spawn`; no fs/network/clipboard capabilities granted to the webview. The only spawn is Tauri's own sidecar launch.
- **Sidecar process** — a native child at the same trust level as the app; its own hardening is loopback binding + DPAPI + SQLite ([[Local API Security]], [[DPAPI]]).

## Related

- [[Threat Model]]
- [[Tauri Overview]]
- [[Security Architecture]]

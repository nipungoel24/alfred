---
type: architecture
layer: desktop
status: active
tags:
  - desktop
  - architecture
---

# Tauri Overview

Tauri 2 shell: `desktop/src-tauri/`.

- `src/main.rs` — the full native lifecycle ([[Desktop Architecture]]): sidecar ownership, readiness gate, single instance, graceful shutdown, `backend_info`/`retry_backend` commands.
- `tauri.conf.json` — dev/build commands (`npm --prefix ../frontend`), `frontendDist: ../../frontend/dist`, CSP, hidden-until-ready window, NSIS `currentUser` bundle.
- `capabilities/default.json` — `core:default` only ([[Native Security]]).
- `icons/` — generated placeholder mark (`tools/generate_icons.py`); replace with the approved brand asset when available.

## Related

- [[Sidecar Architecture]]
- [[Windows Lifecycle]]
- [[Windows Packaging]]
- [[Native Security]]

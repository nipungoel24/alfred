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

- `src/main.rs` — builder + shell plugin + sidecar spawn in `setup`; child handle managed by Tauri (killed on exit).
- `tauri.conf.json` — dev URL `http://localhost:5173`, bundled `frontend/dist`, CSP (connect-src limited to localhost:8765/5173), window 1280×850 (min 900×650), NSIS bundle.
- `capabilities/default.json` — `core:default` + `shell:allow-spawn` only.

## Related

- [[Sidecar Architecture]]
- [[Windows Lifecycle]]
- [[Windows Packaging]]
- [[Native Security]]

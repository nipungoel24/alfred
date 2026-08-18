---
type: architecture
layer: desktop
status: active
tags:
  - desktop
  - critical-path
---

# Sidecar Architecture

The backend ships as a native Windows binary next to the Tauri app.

## Build

`backend/build_sidecar.py` (referenced by `main.rs`) produces the FastAPI app as a PyInstaller single-file executable; Tauri's `externalBin: ["binaries/alfred-backend"]` resolves the target-suffixed binary at bundle time (`alfred-backend-x86_64-pc-windows-msvc.spec`).

## Runtime

- Tauri spawns `alfred-backend` in `setup` → binds `127.0.0.1:8765`.
- The webview talks to it over the CSP-approved localhost origin ([[Local API Security]]).
- App exit → Tauri terminates the child (handle is `app.manage`d).

## Verification status

Binary built; NSIS packaging + native QA not yet verified in this repo's history ([[Project Status]]).

## Related

- [[Tauri Overview]]
- [[Building Backend Sidecar]]
- [[Runtime Lifecycle]]

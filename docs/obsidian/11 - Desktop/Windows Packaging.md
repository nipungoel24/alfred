---
type: architecture
layer: desktop
status: active
tags:
  - desktop
---

# Windows Packaging

Bundle configuration as it exists today.

- Target: **NSIS** installer (`.exe`), per `tauri.conf.json`.
- Frontend: `npm run build` → `frontend/dist` embedded; dev mode points at Vite.
- Sidecar: `binaries/alfred-backend` (PyInstaller single-file) included via `externalBin`.
- Window: 1280×850 default, 900×650 minimum.
- Identifier: `com.alfred.local`, product name "Alfred".

## Status

Config + binary build exist; a full packaged-bundle QA pass is outstanding ([[Project Status]]). Steps to produce the installer live in [[Building Backend Sidecar]] and [[Release Checklist]].

## Related

- [[Sidecar Architecture]]
- [[Tauri Overview]]

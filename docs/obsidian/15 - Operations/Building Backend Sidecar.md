---
type: operations
layer: desktop
status: active
tags:
  - desktop
---

# Building Backend Sidecar

The FastAPI backend compiles to a native Windows binary for Tauri.

## Build

PyInstaller spec: `alfred-backend-x86_64-pc-windows-msvc.spec` at the repo root; `backend/build_sidecar.py` orchestrates the build. Output lands in `desktop/src-tauri/binaries/` (Tauri resolves the target-suffixed name via `externalBin`).

## Notes

- The binary embeds Python + dependencies; rebuild after backend changes.
- DPAPI works identically in the sidecar (it is a normal Windows process) — see [[DPAPI]].

## Related

- [[Sidecar Architecture]]
- [[Windows Packaging]]
- [[Release Checklist]]

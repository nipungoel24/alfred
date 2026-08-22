---
type: architecture
layer: desktop
status: active
tags:
  - desktop
---

# Windows Packaging

Bundle configuration and verified release facts (v0.1.0).

- Target: **NSIS**, `installMode: currentUser` → `%LOCALAPPDATA%\Alfred`, no elevation, Start Menu shortcut + HKCU uninstall registration ([[ADR-017 - Per-User Installer]]).
- Frontend: `npm run build` → `frontend/dist` embedded; dev mode points at Vite.
- Sidecar: `binaries/alfred-backend` (single-file, config embedded — [[Sidecar Architecture]]).
- Icons: generated placeholder set in `desktop/src-tauri/icons/` (`tools/generate_icons.py`) until the approved brand asset replaces it.
- Window: 1280×850 default, 900×650 minimum, hidden until backend readiness.
- Shortcut repair: `desktop/src-tauri/nsis-hooks.nsh` recreates Start Menu/Desktop shortcuts on install/update to avoid stale absolute targets from prior current-user installs.

## Verified artifacts

- Installer: `desktop/src-tauri/target/release/bundle/nsis/Alfred_0.1.0_x64-setup.exe`
- Installed-app checks must be performed from the actual Start Menu shortcut. A previous verification was revoked after the human-visible shortcut still targeted a stale profile path.
- **Signing: UNSIGNED DEVELOPMENT RELEASE** — no Authenticode certificate configured; SmartScreen will warn. Real signing is a release-blocking item for distribution.

## Related

- [[Sidecar Architecture]]
- [[Tauri Overview]]
- [[Release Checklist]]

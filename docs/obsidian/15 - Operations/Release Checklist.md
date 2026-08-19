---
type: operations
layer: meta
status: active
tags:
  - backend
---

# Release Checklist

Ordered pre-release gate for a Windows release (v0.1.0 status: see [[Project Status]]).

1. **Tests** — `py -3 -m pytest backend/tests -q`; frontend `npm test -- --run`, `npm run lint`, `npm run build`; Rust `cargo fmt --check`, `cargo check`, `cargo clippy` (from `desktop/src-tauri`); docs `--check` + `validate_vault.py`.
2. **Real-mailbox smoke** — incremental sync through the packaged sidecar (0 duplicates), one backfill page, category counts sane ([[Gmail E2E Testing]]).
3. **No secrets** — release config embedded at build time only; never commit `production.env` ([[Sidecar Architecture]]).
4. **Sidecar** — `py backend/build_sidecar.py` (embeds release config from `backend/.env`).
5. **Bundle** — `cargo tauri build` → NSIS `Alfred_0.1.0_x64-setup.exe`.
6. **Install** — silent install; verify Start Menu, uninstall registration, installed-app launch, close/reopen, second instance, uninstall-preserves-data.
7. **Signing** — Authenticode certificate required before public distribution (currently UNSIGNED DEVELOPMENT RELEASE, [[Windows Packaging]]).
8. **Theme QA** — both themes across all screens at 1280/1440/1920.

## Related

- [[Running Alfred]]
- [[Development Setup]]
- [[Building Backend Sidecar]]

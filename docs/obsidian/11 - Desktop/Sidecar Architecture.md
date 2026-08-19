---
type: architecture
layer: desktop
status: active
tags:
  - desktop
  - critical-path
---

# Sidecar Architecture

The backend ships as a native Windows binary beside the Tauri app — with its release configuration embedded.

## Build

`backend/build_sidecar.py` runs PyInstaller (`--onefile --noconsole`), embeds `production.env` (Gmail OAuth client + Ollama config, sourced from the build environment's `backend/.env`) into the executable via `--add-data`, and drops `alfred-backend-x86_64-pc-windows-msvc.exe` into `desktop/src-tauri/binaries/`. The installed app therefore needs **no** source tree, no `backend/.env`, no Python (`backend/build_sidecar.py` (see [[Sidecar Architecture]])).

## Runtime

- Tauri spawns it with `ALFRED_HOST=127.0.0.1`, `ALFRED_PORT=<free port>`, `ALFRED_RUNTIME_TOKEN=<per-launch secret>` ([[ADR-015 - Desktop Session Authentication]]).
- `backend/sidecar.py` routes the windowed (console-less) stdout/stderr to devnull so the headless server never crashes on logging.
- Graceful shutdown via `POST /api/shutdown` (workers stop, SQLite closes, exit 0) followed by the shell killing the child ([[ADR-016 - Tauri-Owned Sidecar Lifecycle]]).

## Configuration resolution ([[backend.app.config]])

Frozen builds read `production.env` from (in order): PyInstaller `_MEIPASS`, the exe directory, `resources/`. Dev reads `backend/.env`.

## Verification status

Rebuilt + exercised against the real AppData: health, DPAPI decrypt, Gmail incremental sync (0 duplicates), Ollama analysis, briefing ([[Project Status]]).

## Related

- [[Tauri Overview]]
- [[Building Backend Sidecar]]
- [[Windows Packaging]]

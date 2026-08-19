---
type: adr
layer: meta
status: active
tags:
  - architecture
  - desktop
  - critical-path
---

# ADR-016 - Tauri-Owned Sidecar Lifecycle

## Status

Accepted

## Context

React must never be able to spawn processes (capability boundary), and the backend must not outlive the app or start before the UI understands its state.

## Decision

Tauri — and only Tauri — spawns, polls, and kills the sidecar:

- spawn with dynamic port + runtime token ([[ADR-015 - Desktop Session Authentication]]);
- poll `/health` for ≤45s, then reveal the window (frontend additionally gates with a "Starting Alfred…" state);
- on failure: reveal the window with a Retry state that re-spawns via the `retry_backend` command (no endless respawn loop — retry is user-initiated);
- on exit: `POST /api/shutdown` (graceful worker stop + SQLite close), then kill the child;
- single instance via `tauri-plugin-single-instance`: a second launch focuses the existing window and exits — no second sidecar, no second DB writer.

## Alternatives Considered

- Frontend spawns backend via shell plugin — rejected: violates least privilege ([[Native Security]]).
- Health polling in React only — rejected: the window would flash a failure state on every cold start.

## Consequences

- The frontend depends on `backend_info`/`retry_backend` commands only; capabilities stay `core:default`.
- Dev workflow unchanged (Vite + `cargo tauri dev`).

## Related Code

- `desktop/src-tauri/src/main.rs`
- [[frontend.src.layout.StartupGate.StartupGate|StartupGate]]
- [[POST --api-shutdown|shutdown endpoint]]

## Related Documentation

- [[Desktop Architecture]]
- [[Windows Lifecycle]]
- [[ADR-015 - Desktop Session Authentication]]

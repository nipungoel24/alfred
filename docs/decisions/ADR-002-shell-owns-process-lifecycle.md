# ADR-002 — The native shell owns process lifecycle

Status: Accepted (reaffirms the existing design; corrects the documentation)
Date: 2026-09-26
Gate: 0

## Context

Alfred runs a Python backend that must be started, supervised, and stopped. The
alternative is a user-facing launch script that spawns a terminal.

The existing repository already chose the shell-owned model: `tauri_plugin_shell`
`externalBin` spawns the sidecar, `BackendSupervisor` polls health, and
`tauri_plugin_single_instance` prevents a second Alfred. That choice is correct and is
kept.

Two things are wrong with the execution, and both are documentation-versus-code
mismatches rather than design failures:

- `docs/obsidian/11 - Desktop/Windows Lifecycle.md:15` says "Ready → window shows" and
  `docs/obsidian/14 - Decisions/ADR-016 - Tauri-Owned Sidecar Lifecycle.md:26` says
  "then reveal the window". **The code never calls `window.show()` on a successful
  handshake.** `tauri.conf.json:20` sets `"visible": false` and the only `show()` in the
  codebase is at `main.rs:481`, inside the single-instance callback. The documented
  behaviour is the required behaviour; the code does not do it.
- Five documents state a 45-second startup timeout. `main.rs:27-29` uses 60 seconds.

## Decision

The Tauri shell exclusively owns backend lifecycle. The window is revealed on a successful
backend handshake, not before and not never. Documents are corrected to match the code,
and the code is corrected to match the documented intent.

Concretely, in Phase 1:

1. The window is shown exactly once, on the first `Ready`, from a single place
2. A `RunEvent::Ready` or equivalent hook is the reveal point, not the single-instance
   callback, which exists for a different purpose
3. `HEALTH_TIMEOUT` and `STARTUP_TIMEOUT` are set to one documented value and every
   document is updated to match
4. `backend/` never spawns `alfred-desktop.exe`; `desktop/` never spawns `python`

## Consequences

- There is exactly one place that knows how to start a backend
- A failure to reveal the window is a startup failure, not a cosmetic bug — it is
  testable
- The single-instance plugin and the reveal hook are separate concerns and must not be
  conflated again

## Rejected

**A user-facing `run_app.bat`.** Rejected: this is exactly the multi-console-window
failure the product must not have.

**Show the window immediately and let the user watch the backend start.** Rejected: an
empty window with a spinner for up to 60 seconds is a worse first impression than a
branded splash, and it hides the readiness state that the user needs to see.

**Keep `"visible": false` and rely on a second launch to reveal it.** Rejected: that is
the current defect. It requires the user to launch Alfred twice, which is an explicit
product requirement failure.

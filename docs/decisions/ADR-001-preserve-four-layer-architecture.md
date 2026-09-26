# ADR-001 — Preserve the four-layer architecture

Status: Accepted
Date: 2026-09-26
Gate: 0

## Context

Alfred is four runtimes: a React frontend, a Rust/Tauri shell, a Python/FastAPI backend,
and an external Ollama process. A plausible reading of "make this production-grade" is to
consolidate them — move the backend into Rust, or drop Tauri, or move the AI calls into
the frontend.

The existing separation is not accidental. It is load-bearing:

- Python owns SQLite, `httpx`, and Pydantic, all of which the product depends on heavily
  and none of which Rust would replace without a rewrite
- The Tauri shell owns process lifecycle, which is the only thing that can guarantee no
  console window and no orphan process
- The frontend is a plain web app, which is what makes browser-mode development possible
- Ollama is external, which is what makes the privacy claim verifiable

## Decision

Preserve all four layers and their boundaries. Do not consolidate.

The frontend must never spawn a process, read a file, or hold a Gmail credential. The
shell must never interpret mail. The backend must never touch the window.

## Consequences

- Two languages and two toolchains remain in the build. Accepted.
- The IPC boundary is real and must be specified, not assumed. `docs/Architecture.md` §6
  does this.
- Backend startup is Python startup. Measured in Gate 4, optimised only if it is
  actually slow.
- The shell/backend contract is a small, stable surface: three Tauri commands and one
  runtime token. Changes to it require updating both sides in the same change.

## Rejected

**Rewrite the backend in Rust.** Would remove the Python dependency and probably improve
startup time. Rejected: it discards 207 passing tests and roughly 5 000 lines of working
Gmail, FTS5, and AI logic. That is a rewrite, which `docs/Rules.md` §1.2 forbids without
evidence that the current design cannot meet the requirement. No such evidence exists —
the actual startup defect is a missing `window.show()` call, not the language.

**Drop Tauri and ship Electron.** Rejected: worse startup, larger bundle, and it would
not fix the single-instance or console-window requirements.

**Move AI calls into the frontend.** Rejected: it would put the Ollama endpoint and model
name in the webview, widening the attack surface for no benefit.

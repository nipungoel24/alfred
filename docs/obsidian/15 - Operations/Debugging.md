---
type: operations
layer: meta
status: active
tags:
  - backend
---

# Debugging

Field manual for the common failure modes.

## "Alfred couldn't start its local service" (StartupGate)

Read the diagnostics FIRST — the failure UI shows a code and the log path:

- **Logs**: `%LOCALAPPDATA%\AlfredData\logs\desktop.log` (shell: spawn/port/PID/probe statuses, child exit codes) and `backend.log` (sidecar: config booleans, DB path, crash categories). Never secrets.
- **BACKEND_TIMEOUT** — the shell probed /health for 45s without a 200. Check `backend.log` for a crash category, or whether the port in `desktop.log` was bound.
- **BACKEND_UNAUTHORIZED** — the webview's token didn't match the sidecar's. Indicates a stale client bootstrap; Retry re-resolves the endpoint.
- **No backend spawn at all** — `desktop.log` `spawned child_pid` missing → sidecar resolution failed (see [[Sidecar Architecture]]).
- **Start Menu target mismatch** — inspect `Alfred.lnk` before launching. Target must be `%LOCALAPPDATA%\Alfred\alfred-desktop.exe`; a stale absolute target to another Windows profile prevents human launches before backend startup begins.
- **Shortcut repair blocked** — if installer/COM updates touch but do not change the `.lnk`, inspect ACL/owner. The sandbox/service identity may only have read/execute while the real user owns the shortcut.

## "AI Offline" chip / analysis stuck

1. `GET /health` → backend `status: ok` with `ai: unavailable` means the shell can open while Ollama isn't reachable.
2. Check Ollama: `ollama serve` running? `ollama list` contains `qwen3:4b`?
3. Check jobs: `jobs` table — `retryable_failed` rows with `error_code` tell you why ([[AI Failure Handling]]).

## Backfill stalled

- `GET /api/accounts/{id}/backfill` — state + `last_error` + counters (sanitized).
- `paused` → resume via [[POST --api-accounts-{account_id}-backfill]]; `failed` → resume re-arms the job; 401 → re-authenticate the account.
- Job row `not_before` in the future = normal rate limiting ([[All Mail Backfill Flow]]).

## Missing/new mail not appearing

- Sync error → [[frontend.src.features.accounts.AccountsPage.AccountsPage|AccountsPage]] banner; cursor state in [[accounts]] (sync_cursor).
- Eligibility: mail moved to Spam/Trash in Gmail legitimately disappears from every view — check `mailbox_state` in [[emails]] before assuming a bug ([[backend.app.mail.eligibility.MailEligibilityPolicy|MailEligibilityPolicy]]).

## Frontend blank / theme weird

- DevTools: Vite proxy not needed (API base is `VITE_ALFRED_API_URL`, default `http://127.0.0.1:8765`; Tauri resolves the dynamic port+token via `backend_info`).
- Theme is applied pre-paint; localStorage `alfred-theme` controls it ([[frontend.src.theme.ThemeProvider.ThemeProvider|ThemeProvider]]).

## Docs drift

- `py tools/docs/generate_knowledge_graph.py --check` fails → regenerate ([[Documentation Conventions]]).

## Related

- [[Running Alfred]]
- [[Gmail Errors]]
- [[AI Failure Handling]]
- [[ADR-018 - Health-Before-Heavy-Startup]]

---
type: operations
layer: meta
status: active
tags:
  - backend
---

# Debugging

Field manual for the common failure modes.

## "AI Offline" chip / analysis stuck

1. `GET /health` → `ai: unavailable` means Ollama isn't reachable.
2. Check Ollama: `ollama serve` running? `ollama list` contains `qwen3:4b`?
3. Check jobs: `jobs` table — `retryable_failed` rows with `error_code` tell you why ([[AI Failure Handling]]).

## Backfill stalled

- `GET /api/accounts/{id}/backfill` — state + `last_error` + counters (sanitized).
- `paused` → resume via [[POST --api-accounts-{account_id}-backfill]]; `failed` → resume re-arms the job; 401 → re-authenticate the account.
- Job row `not_before` in the future = normal rate limiting ([[All Mail Backfill Flow]]).

## Missing/new mail not appearing

- Sync error → [[frontend.src.features.accounts.AccountsPage.AccountsPage|AccountsPage]] banner; cursor state in [[accounts]].
- Eligibility: mail moved to Spam/Trash in Gmail legitimately disappears from every view — check `mailbox_state` in [[emails]] before assuming a bug ([[backend.app.mail.eligibility.MailEligibilityPolicy|MailEligibilityPolicy]]).

## Frontend blank / theme weird

- DevTools: Vite proxy not needed (API base is `VITE_ALFRED_API_URL`, default `http://127.0.0.1:8765`).
- Theme is applied pre-paint; localStorage `alfred-theme` controls it ([[frontend.src.theme.ThemeProvider.ThemeProvider|ThemeProvider]]).

## Docs drift

- `py tools/docs/generate_knowledge_graph.py --check` fails → regenerate ([[Documentation Conventions]]).

## Related

- [[Running Alfred]]
- [[Gmail Errors]]
- [[AI Failure Handling]]

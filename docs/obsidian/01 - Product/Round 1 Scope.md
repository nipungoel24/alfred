---
type: architecture
layer: product
status: active
tags:
  - system
---

# Round 1 Scope

The explicit, enforced boundary of Alfred Round 1. Anything not listed here is out of scope until a future round.

## In scope

| Area | What ships |
|---|---|
| Providers | Gmail only ([[ADR-001 - Gmail Only Round 1]]) |
| Access | Read-only: `gmail.readonly` + `userinfo.email` |
| Mailbox | Active Inbox, All Mail (received+archived+sent), Gmail categories; spam/trash/draft excluded |
| Sync | Initial sync, historyId incremental sync, pagination, progressive All Mail backfill |
| Intelligence | Priority, summary, why-it-matters, needs-reply, deadlines, action items (qwen3:4b local) |
| Projections | Tasks (derived), Deadlines, Needs Reply, Important, Briefing |
| Draft | Local reply draft generation (text output only) |
| Storage | Local SQLite (WAL, FTS5) — [[Database Overview]] |
| Desktop | Tauri shell + FastAPI sidecar ([[Sidecar Architecture]]) |
| UX | Mattered-style mail workspace, Overview, Tasks, Deadlines, Accounts, Settings; light/dark |

## Explicitly out of scope

- **Sending** mail (no Gmail `send` scope, no composer).
- **Editing drafts** in Gmail (generated drafts are local text only).
- **IMAP / Outlook / any second provider.**
- **Cloud AI** — no hosted LLM calls. Ollama is the only inference path.
- **Calendar**, contacts, tasks sync to external services.
- **Multi-account** beyond a single Gmail connection.
- **Spam screen** — spam stays Gmail-managed and invisible to Alfred by design.

## Behavior notes that look like scope but are policy

- Archived mail is visible in All Mail but excluded from briefing/attention/tasks — visibility ≠ intelligence eligibility ([[backend.app.mail.eligibility.MailEligibilityPolicy|MailEligibilityPolicy]]).
- Promotions/Social are analyzed lazily (deferred) — [[ADR-007 - Background Analysis Queue]].
- Sent messages appear in All Mail with a SENT indicator but never generate incoming attention.

## Related

- [[Product Vision]]
- [[ADR Index]]
- [[Project Status]]

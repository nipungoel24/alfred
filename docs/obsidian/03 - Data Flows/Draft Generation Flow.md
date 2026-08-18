---
type: data-flow
layer: ai
status: active
tags:
  - system
  - ai
---

# Draft Generation Flow

Local reply drafting — the only "writing" Alfred does, and it never sends.

1. User opens a message that needs a reply → [[frontend.src.intelligence.IntelligencePanel.IntelligencePanel|IntelligencePanel]] shows *Generate Draft* (gradient primary action).
2. [[POST --api-emails-{email_id}-draft]] → [[POST --api-emails-{email_id}-draft|draft handler]].
3. [[backend.app.ai.service.AIService.draft_reply]] builds bounded thread context: last 3 messages of the thread (300-char body previews each) via [[backend.app.db.repositories.Repository.emails_by_thread]] — sent messages included as context, which is their only intelligence role.
4. Ollama returns plain text (temperature 0.7, no schema) — rendered in the editor-like `draft-panel`.

## Design rules

- **No send**: `gmail.readonly` scope makes sending impossible at the credential level ([[Round 1 Scope]]).
- **Thread context is bounded** — 3 messages × 300 chars, so long threads can't blow the context window.
- **Failure surface** — Ollama down → scoped error banner in the panel only; the rest of the app is untouched ([[AI Failure Handling]]).
- The draft is displayed locally and disappears with the session — no persistence, no Gmail draft write.

## Related

- [[Email Analysis Flow]]
- [[Prompt Architecture]]
- [[frontend.src.mail.MessageReader.MessageReader|MessageReader]]

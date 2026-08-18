---
type: architecture
layer: product
status: active
tags:
  - security
  - system
---

# Privacy Model

Alfred's privacy promise, stated precisely enough to audit.

## What leaves the machine

| Direction | What flows | Why |
|---|---|---|
| → Google | OAuth tokens, Gmail API reads (messages, history, profile) | That is the mailbox itself |
| → Ollama | Email text **after local sanitization** (sender, subject, truncated body) | Local inference only — loopback HTTP `127.0.0.1:11434` |

Nothing else has network access. There is no telemetry, no cloud AI, no analytics endpoint.

## What never leaves the machine

- Email bodies (only sanitized, truncated slices reach the local model).
- Gmail OAuth tokens (DPAPI-encrypted at rest — [[Token Storage]]).
- SQLite data (AppData, local only).
- Analyses, tasks, briefings (all derived locally).

## Local-at-rest posture

- OAuth refresh/access tokens: DPAPI ciphertext in [[credentials]] ([[backend.app.db.secure_store]]).
- Email content: plaintext JSON in [[emails]] — protected only by the OS user account. This is a documented tradeoff; see [[Threat Model]] and [[Data Privacy]].

## The AI boundary

Email content is **untrusted input** to the model. The system prompt forbids instruction-following from mail, bodies are truncated/sanitized before inference, and the LLM's output is schema-validated — see [[Email Content Trust Boundary]] and [[Prompt Injection Defense]].

## Related

- [[Threat Model]]
- [[Security Architecture]]
- [[ADR-004 - Ollama Local AI]]

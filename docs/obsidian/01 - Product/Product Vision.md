---
type: architecture
layer: product
status: active
tags:
  - system
---

# Product Vision

Alfred is a **private executive inbox assistant**. Your mail already contains your commitments, deadlines, and people — but no human can triage a noisy inbox at 8am. Alfred does that triage locally: it mirrors the Gmail state that matters, runs a small private model over new mail, and turns the inbox into a short list of *what actually needs you*: important mail, required replies, real tasks, real deadlines, and a one-paragraph briefing.

## Design principles

1. **Privacy is the product.** Mail never leaves the machine for AI processing. Cloud is only Gmail's own API (fetch, not analyze). See [[Privacy Model]] and [[Threat Model]].
2. **Gmail stays the source of truth.** Alfred never invents mailbox state; it consumes Gmail labels, categories, and history. See [[Gmail Architecture]].
3. **Derived data is disposable, user state is sacred.** Analyses/tasks are projections; the source email rows are never destroyed during derivation upgrades. See [[Data Ownership]] and [[ADR-009 - Versioned Task Derivation]].
4. **The intelligence earns its place.** Promotions are not force-fed to the briefing; deferred analysis keeps Ollama focused on what matters. See [[AI Architecture]] and [[backend.app.mail.eligibility.MailEligibilityPolicy|MailEligibilityPolicy]].
5. **Feels like premium software.** Mattered-style mail workspace, Siri-like ambient calm, Apple-grade polish — see [[Design System]].

## Experience pillars

- **Inbox** — Gmail tabs (Primary/Promotions/Social/Updates/Forums) with live counts, virtualized rows, real actions only.
- **All Mail** — the complete local mirror (received + archived + sent), progressively synced by the backend.
- **Alfred Intelligence** — a companion pane per message: summary, why it matters, priority, tasks, deadlines, reply draft.
- **Overview** — a morning command center: greeting, metrics, needs-attention, upcoming, briefing.
- **Tasks / Deadlines** — the derived projections, reconciled with user state.

## Non-goals

Sending mail, composing from scratch, calendar, contacts, multi-provider mail, cloud models, and "AI-written-your-emails" features. Alfred advises; it does not act on Gmail (read-only scope). See [[Round 1 Scope]].

## Related

- [[System Architecture]]
- [[ADR Index]]
- [[User Journeys]]

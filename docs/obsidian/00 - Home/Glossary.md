---
type: architecture
layer: meta
status: active
tags:
  - documentation
---

# Glossary

Alfred-specific terminology, each entry linked to its implementation.

## Core entities

- **Email** — the normalized local message: [[backend.app.schemas.Email]]. Stored as JSON in [[emails]].
- **EmailAnalysis** — the structured AI verdict for one email: [[backend.app.schemas.EmailAnalysis]]. Stored in [[email_analysis]], keyed by content fingerprint.
- **InboxBriefing** — the daily executive summary: [[backend.app.schemas.InboxBriefing]], produced by [[backend.app.ai.service.AIService.generate_inbox_briefing]], cached in [[inbox_briefing]].
- **Task** — a derived, user-actionable projection: [[backend.app.schemas.Task]], stored in [[tasks]]. See [[ADR-008 - Separate Action Candidates From Tasks]].
- **ActionCandidate** — an action item *inside* an analysis (raw LLM output). Only validated candidates become Tasks via [[backend.app.services.task_derivation.derive_tasks]].

## Identity & deduplication

- **Task fingerprint** — stable SHA-256 of `thread_id + normalized action` used for deduplication: [[backend.app.services.task_derivation.task_fingerprint]].
- **Content fingerprint** — SHA-256 of sender+subject+body+timestamp; the analysis cache key: [[backend.app.mail.fingerprint.content_fingerprint]].
- **Derivation version** — schema version of the task-derivation rules; lets old derivations be rebuilt safely: `DERIVATION_VERSION` in [[backend.app.services.task_derivation]] and [[ADR-009 - Versioned Task Derivation]].

## Gmail

- **historyId** — Gmail's opaque incremental-sync cursor. Stored in the account [[Glossary|sync cursor]] JSON.
- **Sync cursor** — per-account JSON: `{history_id, next_page_token, backfill_state, …}` persisted in [[accounts]].
- **Mailbox state** — derived per message from Gmail label IDs: [[backend.app.mail.eligibility.MailboxState]] (active_inbox / archived / spam / trash / sent / draft).
- **Pipeline eligibility** — whether a message may feed Alfred intelligence: [[backend.app.mail.eligibility.PipelineEligibility]] (active / deferred / excluded). Central policy: [[backend.app.mail.eligibility.MailEligibilityPolicy]].
- **Gmail category** — the Gmail tab mapping (primary/promotions/social/updates/forums): [[backend.app.mail.eligibility.GmailCategory]]. Never re-derived with the LLM.
- **Backfill state** — typed progress of the All Mail import: [[backend.app.mail.eligibility.BackfillState]] + [[backend.app.mail.backfill.normalize_cursor]]. See [[All Mail Backfill Flow]].

## Infrastructure

- **Sidecar** — the FastAPI backend compiled to a native binary and spawned by Tauri: [[Sidecar Architecture]].
- **DPAPI** — Windows Data Protection API used to encrypt OAuth tokens: [[DPAPI]], [[backend.app.db.secure_store.encrypt_token]].
- **SSE** — Server-Sent Events used for live analysis progress: [[SSE Progress Flow]].
- **React Query** — frontend data layer: [[ADR-010 - React Query]].
- **Structured output** — Ollama's `format` parameter fed with a JSON Schema so the model returns valid JSON: [[Structured Output]].
- **Analysis job** — a durable row in [[jobs]] describing one email to analyze: [[Background Analysis Job Flow]].

---
type: architecture
layer: ai
status: active
tags:
  - ai
---

# AI Caching

The cache layer that keeps Ollama quiet when nothing changed.

## Analysis cache ([[email_analysis]])

- Key: `(email_id, content_hash, model_name, schema_version)` — the content fingerprint covers sender/subject/body/timestamp ([[backend.app.mail.fingerprint.content_fingerprint]]).
- Lookup happens in the worker *before* inference; a hit still triggers task derivation (cheap, local).
- Deliberately NOT keyed by prompt version: prompt changes don't auto-bust caches — schema version does. See [[Prompt Architecture]] for the reasoning.

## Briefing cache ([[inbox_briefing]])

- Key: hash of the *analyses* of the eligible set + schema version + model ([[backend.app.mail.briefing_fingerprint.briefing_fingerprint]]) — any new mail/analysis/eligibility change produces a new fingerprint.

## Non-caches by design

- Draft generation is on-demand and uncached (fresh context each time).
- Eligibility/state changes never delete cached analyses — projections hide them instead ([[Data Ownership]]).

## Related

- [[Email Analysis Flow]]
- [[Briefing Generation Flow]]
- [[email_analysis]]

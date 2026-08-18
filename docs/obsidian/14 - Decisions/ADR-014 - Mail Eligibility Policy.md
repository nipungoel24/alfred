---
type: adr
layer: meta
status: active
tags:
  - architecture
  - gmail
  - critical-path
---

# ADR-014 - Mail Eligibility Policy

## Status

Accepted

## Context

Early filtering was scattered: routes, sync, and workers each had their own "is this spam?" logic, and stale analyses of mail that had since moved to Spam kept polluting the briefing.

## Decision

One module — [[backend.app.mail.eligibility.MailEligibilityPolicy|MailEligibilityPolicy]] — owns: mailbox state derivation from Gmail label IDs, Gmail tab categories, pipeline eligibility (active/deferred/excluded), briefing inclusion, and analysis scheduling priority. Persisted projections (`mailbox_state`, `gmail_category`, `pipeline_eligibility` on [[emails]]) are derived at write time and recomputed on label history events.

## Why

One policy = one place to reason about "source email data ≠ active Alfred attention data" ([[Data Ownership]]); no `if "SPAM" not in labels` scattered across twelve files.

## Consequences

- Visibility (All Mail) and intelligence eligibility are deliberately decoupled: archived/sent mail is visible but never feeds attention.
- Gmail's own categories are authoritative — the LLM never re-classifies tabs ([[backend.app.mail.eligibility.GmailCategory|GmailCategory]]).

## Related Code

- [[backend.app.mail.eligibility]]
- [[backend.app.db.repositories.Repository.update_email_labels|update_email_labels]]

## Related Documentation

- [[Gmail Architecture]]
- [[Data Ownership]]

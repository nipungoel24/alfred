---
type: architecture
layer: gmail
status: active
tags:
  - gmail
  - architecture
---

# Gmail Overview

Everything Alfred knows about your mailbox comes from the Gmail API, read-only. All of it lives in one provider class and one policy module.

## The provider ([[backend.app.mail.providers.gmail.GmailProvider|GmailProvider]])

- OAuth lifecycle ([[Google OAuth]])
- `sync_messages` — initial + incremental ([[History Sync]])
- `backfill_messages` — progressive All Mail ([[All Mail Backfill Flow]])
- `refresh_message_labels` — METADATA-only label refresh
- `_normalize_message` — MIME → [[backend.app.schemas.Email|Email]] + label IDs ([[MIME Parsing]])
- `_ensure_access_token` — transparent refresh

## The policy ([[backend.app.mail.eligibility.MailEligibilityPolicy|MailEligibilityPolicy]])

Turns raw label IDs into product semantics: mailbox state, Gmail tab category, pipeline eligibility, briefing inclusion, scheduling priority ([[Gmail Architecture]]).

## Deep dives

- [[Google OAuth]]
- [[Token Storage]]
- [[DPAPI]]
- [[MIME Parsing]]
- [[History Sync]]
- [[Pagination]]
- [[Gmail Errors]]

## Related

- [[Gmail Architecture]]
- [[Gmail OAuth Flow]]
- [[Gmail Incremental Sync Flow]]

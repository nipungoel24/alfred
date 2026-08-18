---
type: adr
layer: meta
status: active
tags:
  - architecture
  - gmail
---

# ADR-001 - Gmail Only Round 1

## Status

Accepted

## Context

Alfred must be a focused product: a smart inbox for the owner's real mail. Multiple providers multiply OAuth, sync, and mapping complexity before any value is proven.

## Decision

Round 1 supports **Gmail only**, read-only (`gmail.readonly` + `userinfo.email`). No IMAP, no Outlook, no sending.

## Alternatives Considered

- Multi-provider abstraction from day one ([[backend.app.mail.providers.base.MailProvider]] exists as an interface) — deferred until a second provider is justified.

## Why

One provider = one sync model (historyId), one category model (CATEGORY_* labels), one credential story (DPAPI). The provider interface keeps the door open without paying for it now.

## Consequences

- Mailbox semantics (labels, categories, history) are Gmail-shaped and documented as such ([[Gmail Architecture]]).
- Sending/drafts editing are impossible by scope — treated as a feature ([[Round 1 Scope]]).

## Related Code

- [[backend.app.mail.providers.gmail.GmailProvider|GmailProvider]]
- [[backend.app.mail.providers.base.MailProvider|MailProvider]]

## Related Documentation

- [[Gmail Overview]]
- [[Round 1 Scope]]

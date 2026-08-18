---
type: architecture
layer: test
status: active
tags:
  - test
  - gmail
---

# Gmail E2E Testing

How the real mailbox is validated without ever resetting it.

## Principles

- **Never delete, never reset** — validation runs incremental sync and reads counts.
- **Sanitized reporting only** — counts and internal ids; no subjects, no senders, no bodies.
- **No visual QA without the user** — private mail never enters docs or logs.

## Acceptance checks performed (evidence in [[Project Status]])

- Incremental sync imports new inbox mail; label history moves spam out of every projection and back on restore.
- Progressive All Mail backfill: first page fast, older pages append, zero duplicates, cursor persists, restart resumes, frontend absence doesn't pause the loop.
- Category counts (Primary/Promotions/Social/Updates/Forums) derived from real labels; spam/trash never appear.
- Archived visible in All Mail, invisible to intelligence; Sent visible with badge, zero incoming attention.

## Related

- [[Testing Strategy]]
- [[All Mail Backfill Flow]]
- [[Gmail Incremental Sync Flow]]

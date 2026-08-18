---
type: architecture
layer: frontend
status: active
tags:
  - frontend
---

# Email Reader Screen

[[frontend.src.mail.MessageReader.MessageReader|MessageReader]] — the email as a document.

## Anatomy

1. **Sticky toolbar** — frosted, real actions only: Later (persisted toggle), Copy (clipboard with fallback + "Copied" feedback), Intelligence toggle.
2. **Document surface** — `reader-surface` card: light `#fdfdfc` / dark `#151a24`, 1px border, soft shadow, 14px radius, max-width 800px (~75–85 chars/line), independent scroll with 28–44px workspace padding.
3. **Header block** — subject (23px, tight tracking) → avatar (deterministic gradient from sender hash) + sender + recipients + formatted date → hairline divider.
4. **Body** — 15.5px / 1.66 line-height, `pre-wrap`, `overflow-wrap: anywhere` (long URLs wrap), empty-body placeholder. Rendered as escaped text only — no HTML execution.
5. **Attachments** — quiet tile inside the document with size metadata (no fake download actions).

## States

Empty (no selection), loading (skeletons mirror the document layout), error ("Couldn't load this message — may have been removed from Gmail"), loaded.

## Related

- [[MIME Parsing]] (why body is plain text)
- [[Mail Workspace Screen]]
- [[Design System]]

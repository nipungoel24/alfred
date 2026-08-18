---
type: architecture
layer: gmail
status: active
tags:
  - gmail
  - security
---

# MIME Parsing

How a Gmail message becomes Alfred's plain-text [[backend.app.schemas.Email|Email]].

## Pipeline ([[backend.app.mail.providers.gmail.GmailProvider]])

1. Headers → dict (lowercased names): `From` (name/email split), `To`, `Subject`.
2. `payload.parts` walked recursively: `text/plain` preferred over `text/html`; missing parts fall through to the top-level body.
3. Base64url decode (UTF-8, errors replaced).
4. HTML → text via `_clean_html`: script/style blocks stripped, block elements become newlines, remaining tags removed, entities unescaped, per-line whitespace collapsed.
5. `labelIds` collected as first-class data; `source_metadata.gmail_raw` keeps a lean digest (labels, size, snippet) — never the raw base64 payload twice.

## Trust posture

Parsing is *sanitization*: by the time content reaches SQLite it is plain text, and by the time it reaches the model it is truncated further ([[Email Content Trust Boundary]], [[Prompt Injection Defense]]). The frontend renders body text only (React-escaped) — no HTML rendering path exists.

## Related

- [[Gmail Overview]]
- [[emails]]
- [[Email Content Trust Boundary]]

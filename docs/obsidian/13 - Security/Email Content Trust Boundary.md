---
type: security
layer: security
status: active
tags:
  - security
  - critical-path
---

# Email Content Trust Boundary

Mail is **untrusted input**, full stop. Every hop it takes shrinks its power.

1. **Wire → cache** ([[MIME Parsing]]): HTML stripped server-side; only plain text + labels persist in [[emails]].
2. **Cache → model** ([[Prompt Architecture]]): bodies truncated to 2000 chars, quoted/base64/URL noise removed, prompt rules forbid following mail instructions ([[Prompt Injection Defense]]).
3. **Model → product** ([[Structured Output]]): fixed JSON schema; no actuators — output can only create local derived rows.
4. **Cache → UI**: React renders text only (auto-escaped); no `dangerouslySetInnerHTML` exists in the codebase.

## Why this holds

Even a perfectly crafted malicious email can at worst produce a nonsense analysis or a spurious task — both user-deletable, neither capable of sending mail, touching credentials, or executing code ([[Round 1 Scope]], [[Threat Model]]).

## Related

- [[MIME Parsing]]
- [[Prompt Injection Defense]]
- [[Email Reader Screen]]

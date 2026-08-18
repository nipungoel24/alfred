---
type: architecture
layer: ai
status: active
tags:
  - ai
---

# Analysis Schema

The per-email AI contract — [[backend.app.schemas.EmailAnalysis]] and its parts.

| Field | Type | Meaning | Constraints in prompt |
|---|---|---|---|
| `short_summary` | str | one/two-line executive summary | no invented facts |
| `category` | [[backend.app.schemas.Category]] | semantic category (work/personal/finance/…) — NOT the Gmail tab ([[backend.app.mail.eligibility.GmailCategory|GmailCategory]]) | fixed enum |
| `priority` | [[backend.app.schemas.Priority]] | urgent/high/medium/low | score bands: urgent 85–100, high 65–84, medium 30–64, low 0–29 |
| `priority_score` | int 0–100 | numeric ranking | must match band |
| `reason_for_priority` | str | "why it matters" line | concise |
| `needs_reply` | bool | does the user owe a reply | receipts/newsletters → false |
| `action_items` | [[backend.app.schemas.ActionItem]][] | raw candidates — NOT tasks | owner "user" for direct requests; no marketing CTAs |
| `deadlines` | [[backend.app.schemas.Deadline]][] | explicit deadlines only | relative wording preserved; ambiguous timing omitted |

## Two-layer semantics

The schema output is an **analysis**; tasks are a *projection* with additional gates ([[Task Derivation Flow]]). The schema's `category` is semantic intelligence and deliberately separate from Gmail's tab categories ([[backend.app.mail.eligibility.GmailCategory|GmailCategory]]) — Gmail classifies tabs, the model classifies meaning.

## Related

- [[Structured Output]]
- [[Prompt Architecture]]
- [[backend.app.schemas]]

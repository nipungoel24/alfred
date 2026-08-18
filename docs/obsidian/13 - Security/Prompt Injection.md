---
type: security
layer: security
status: active
tags:
  - security
---

# Prompt Injection

Alfred's complete prompt-injection defense story — consolidated.

- Full breakdown: [[Prompt Injection Defense]]
- The trust boundary it defends: [[Email Content Trust Boundary]]
- Residual risk statement: [[Threat Model]]

Quick reference: sanitize → truncate → instruct → constrain schema → gate derivation → no actuators. The model has nothing to hijack *into*: no send, no tools, no filesystem writes beyond derived rows.

## Related

- [[Prompt Architecture]]
- [[AI Architecture]]

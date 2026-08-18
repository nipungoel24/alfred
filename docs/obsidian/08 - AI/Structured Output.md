---
type: architecture
layer: ai
status: active
tags:
  - ai
---

# Structured Output

Alfred never parses prose from the model for analysis — it constrains the model to a schema.

## Mechanism

Ollama's `format` parameter accepts a JSON Schema. Alfred passes `EmailAnalysis.model_json_schema()` (Pydantic v2) directly — the same schema that validates the result. See [[backend.app.ai.ollama_client.OllamaClient.generate]].

## The schemas

- [[backend.app.schemas.EmailAnalysis]] — summary, category, priority (+score 0–100), why-it-matters, needs_reply, action_items, deadlines.
- [[backend.app.schemas.InboxBriefing]] — executive summary + items; counts are recomputed locally regardless ([[Briefing Generation Flow]]).

## Enforcement chain

1. Prompt instructs: "return only JSON matching the supplied schema" ([[Prompt Architecture]]).
2. Ollama `format` biases generation toward valid JSON.
3. `model_validate_json` — malformed output raises → [[backend.app.ai.ollama_client.OllamaInvalidResponse]] → job fails cleanly.
4. Post-validation guards: meta-language and ISO-timestamp sanitization for briefings; priority-score bands cross-checked in prompts.

## Related

- [[Analysis Schema]]
- [[Prompt Architecture]]
- [[AI Failure Handling]]

---
type: architecture
layer: test
status: active
tags:
  - test
  - ai
---

# AI Testing

Testing the intelligence layer without testing the model.

| Layer | Tested | How |
|---|---|---|
| Transport | error taxonomy, metrics parsing | [[backend.tests.test_ollama_mock]] |
| Contract | schema validation, structured-output failure path | same + [[backend.tests.test_golden_corpus]] |
| Prompts | body sanitization (quotes/base64/URLs/truncation), injection clauses present | corpus + [[backend.tests.test_extended]] (malicious HTML) |
| Derivation | gates downstream of analysis | [[backend.tests.test_task_derivation]] |
| Briefing | local count overrides, meta-language guard | [[backend.tests.test_extended]] API flow |
| Failure UX | Ollama-down behavior | mocked client errors → worker retryable/failed states |

## Deliberate non-goal

No benchmark-quality assertions on model output text — the golden corpus pins *behavior contracts*, not prose.

## Related

- [[AI Failure Handling]]
- [[Golden Email Corpus]]
- [[Testing Strategy]]

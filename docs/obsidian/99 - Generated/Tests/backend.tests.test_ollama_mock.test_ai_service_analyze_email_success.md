---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_ollama_mock
qualified_name: backend.tests.test_ollama_mock.test_ai_service_analyze_email_success
source: backend/tests/test_ollama_mock.py
line: 65
status: active
tags: [test, function, test]
---

# test_ai_service_analyze_email_success

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_ai_service_analyze_email_success` in `backend/tests/test_ollama_mock.py`.

## Location

`backend/tests/test_ollama_mock.py:65`

## Signature

```python
()
```

## Calls

- `run` (`asyncio.run`, calls-inferred)
- [[backend.app.ai.ollama_client.InferenceMetrics|InferenceMetrics]] (calls)
- [[backend.app.ai.ollama_client.OllamaClient|OllamaClient]] (calls)
- [[backend.app.ai.service.AIService|AIService]] (calls)
- [[backend.app.schemas.Email|Email]] (calls)
- `dumps` (`json.dumps`, calls-inferred)
- `AsyncMock` (`unittest.mock.AsyncMock`, calls-inferred)
- `object` (`unittest.mock.patch.object`, calls-inferred)

## Side Effects

- network (HTTP)

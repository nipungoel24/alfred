---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.tests.test_ollama_mock
source: backend/tests/test_ollama_mock.py
status: active
tags: [module, backend]
---

# backend.tests.test_ollama_mock

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/tests/test_ollama_mock.py`

## Imports

- `AIService` ← `backend.app.ai.service.AIService`
- `AsyncMock` ← `unittest.mock.AsyncMock`
- `Category` ← `backend.app.schemas.Category`
- `Email` ← `backend.app.schemas.Email`
- `EmailAnalysis` ← `backend.app.schemas.EmailAnalysis`
- `InferenceMetrics` ← `backend.app.ai.ollama_client.InferenceMetrics`
- `MagicMock` ← `unittest.mock.MagicMock`
- `OllamaClient` ← `backend.app.ai.ollama_client.OllamaClient`
- `OllamaUnavailable` ← `backend.app.ai.ollama_client.OllamaUnavailable`
- `Priority` ← `backend.app.schemas.Priority`
- `asyncio` ← `asyncio`
- `httpx` ← `httpx`
- `json` ← `json`
- `patch` ← `unittest.mock.patch`
- `pytest` ← `pytest`

## Tests

- [[backend.tests.test_ollama_mock.test_ai_service_analyze_email_success|test_ai_service_analyze_email_success]]
- [[backend.tests.test_ollama_mock.test_ollama_client_empty_response|test_ollama_client_empty_response]]
- [[backend.tests.test_ollama_mock.test_ollama_client_http_error|test_ollama_client_http_error]]
- [[backend.tests.test_ollama_mock.test_ollama_client_sends_correct_payload|test_ollama_client_sends_correct_payload]]

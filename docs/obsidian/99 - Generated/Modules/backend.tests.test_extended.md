---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.tests.test_extended
source: backend/tests/test_extended.py
status: active
tags: [module, backend]
---

# backend.tests.test_extended

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/tests/test_extended.py`

## Imports

- `AIService` ← `backend.app.ai.service.AIService`
- `AsyncMock` ← `unittest.mock.AsyncMock`
- `BRIEFING_SCHEMA_VERSION` ← `backend.app.mail.briefing_fingerprint.BRIEFING_SCHEMA_VERSION`
- `Category` ← `backend.app.schemas.Category`
- `Deadline` ← `backend.app.schemas.Deadline`
- `Email` ← `backend.app.schemas.Email`
- `EmailAnalysis` ← `backend.app.schemas.EmailAnalysis`
- `InboxBriefing` ← `backend.app.schemas.InboxBriefing`
- `MagicMock` ← `unittest.mock.MagicMock`
- `OllamaClient` ← `backend.app.ai.ollama_client.OllamaClient`
- `OllamaUnavailable` ← `backend.app.ai.ollama_client.OllamaUnavailable`
- `Path` ← `pathlib.Path`
- `Priority` ← `backend.app.schemas.Priority`
- `Repository` ← `backend.app.db.repositories.Repository`
- `TestClient` ← `fastapi.testclient.TestClient`
- `asyncio` ← `asyncio`
- `briefing_fingerprint` ← `backend.app.mail.briefing_fingerprint.briefing_fingerprint`
- `content_fingerprint` ← `backend.app.mail.fingerprint.content_fingerprint`
- `httpx` ← `httpx`
- `json` ← `json`
- `normalized_email` ← `backend.app.mail.normalizer.normalized_email`
- `os` ← `os`
- `patch` ← `unittest.mock.patch`
- `pytest` ← `pytest`

## Functions

- [[backend.tests.test_extended.get_analysis|get_analysis]]
- [[backend.tests.test_extended.get_email|get_email]]

## Tests

- [[backend.tests.test_extended.test_ambiguous_deadline_handling|test_ambiguous_deadline_handling]]
- [[backend.tests.test_extended.test_api_endpoint_flows|test_api_endpoint_flows]]
- [[backend.tests.test_extended.test_briefing_deadline_aggregation|test_briefing_deadline_aggregation]]
- [[backend.tests.test_extended.test_cache_hit_and_invalidation|test_cache_hit_and_invalidation]]
- [[backend.tests.test_extended.test_explicit_deadline_schema_handling|test_explicit_deadline_schema_handling]]
- [[backend.tests.test_extended.test_malformed_json_response|test_malformed_json_response]]
- [[backend.tests.test_extended.test_malicious_html_normalization|test_malicious_html_normalization]]
- [[backend.tests.test_extended.test_model_unavailable|test_model_unavailable]]
- [[backend.tests.test_extended.test_ollama_empty_response|test_ollama_empty_response]]
- [[backend.tests.test_extended.test_persistence_restart|test_persistence_restart]]
- [[backend.tests.test_extended.test_prompt_injection_safety|test_prompt_injection_safety]]

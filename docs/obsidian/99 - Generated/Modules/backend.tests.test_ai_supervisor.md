---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.tests.test_ai_supervisor
source: backend/tests/test_ai_supervisor.py
status: active
tags: [module, backend]
---

# backend.tests.test_ai_supervisor

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/tests/test_ai_supervisor.py`

## Imports

- `AIState` ← `backend.app.ai.supervisor.AIState`
- `AISupervisor` ← `backend.app.ai.supervisor.AISupervisor`
- `OllamaClient` ← `backend.app.ai.ollama_client.OllamaClient`
- `OllamaModelMissing` ← `backend.app.ai.ollama_client.OllamaModelMissing`
- `OllamaTimeout` ← `backend.app.ai.ollama_client.OllamaTimeout`
- `OllamaUnavailable` ← `backend.app.ai.ollama_client.OllamaUnavailable`
- `Path` ← `pathlib.Path`
- `asyncio` ← `asyncio`
- `find_ollama_executable` ← `backend.app.ai.supervisor.find_ollama_executable`
- `pytest` ← `pytest`

## Classes

- [[backend.tests.test_ai_supervisor.FakeClient|FakeClient]]

## Functions

- [[backend.tests.test_ai_supervisor.FakeClient.__init__|__init__]]
- [[backend.tests.test_ai_supervisor.FakeClient.generate|generate]]
- [[backend.tests.test_ai_supervisor.FakeClient.health|health]]
- [[backend.tests.test_ai_supervisor._noop_auto_start|_noop_auto_start]]
- [[backend.tests.test_ai_supervisor.make_supervisor|make_supervisor]]
- [[backend.tests.test_ai_supervisor.run|run]]

## Tests

- [[backend.tests.test_ai_supervisor.test_backoff_is_bounded|test_backoff_is_bounded]]
- [[backend.tests.test_ai_supervisor.test_failure_classification|test_failure_classification]]
- [[backend.tests.test_ai_supervisor.test_find_ollama_executable_returns_none_when_absent|test_find_ollama_executable_returns_none_when_absent]]
- [[backend.tests.test_ai_supervisor.test_model_missing_state|test_model_missing_state]]
- [[backend.tests.test_ai_supervisor.test_ollama_not_running_state|test_ollama_not_running_state]]
- [[backend.tests.test_ai_supervisor.test_ready_requires_smoke_test|test_ready_requires_smoke_test]]
- [[backend.tests.test_ai_supervisor.test_recovery_flow_resumes_queue|test_recovery_flow_resumes_queue]]
- [[backend.tests.test_ai_supervisor.test_smoke_prompt_never_contains_user_data|test_smoke_prompt_never_contains_user_data]]
- [[backend.tests.test_ai_supervisor.test_state_change_callbacks|test_state_change_callbacks]]

---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.app.ai.supervisor
source: backend/app/ai/supervisor.py
status: active
tags: [module, backend]
---

# backend.app.ai.supervisor

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/app/ai/supervisor.py`

## Imports

- `Callable` ← `typing.Callable`
- `OllamaClient` ← `backend.app.ai.ollama_client.OllamaClient`
- `OllamaInsufficientSpace` ← `backend.app.ai.ollama_client.OllamaInsufficientSpace`
- `OllamaModelMissing` ← `backend.app.ai.ollama_client.OllamaModelMissing`
- `OllamaPullFailed` ← `backend.app.ai.ollama_client.OllamaPullFailed`
- `OllamaTimeout` ← `backend.app.ai.ollama_client.OllamaTimeout`
- `OllamaUnavailable` ← `backend.app.ai.ollama_client.OllamaUnavailable`
- `PullProgress` ← `backend.app.ai.ollama_client.PullProgress`
- `asyncio` ← `asyncio`
- `check_for_model_download` ← `backend.app.ai.resources.check_for_model_download`
- `human_bytes` ← `backend.app.ai.resources.human_bytes`
- `logging` ← `logging`
- `os` ← `os`
- `shutil` ← `shutil`
- `subprocess` ← `subprocess`
- `sys` ← `sys`

## Classes

- [[backend.app.ai.supervisor.AIState|AIState]]
- [[backend.app.ai.supervisor.AISupervisor|AISupervisor]]

## Functions

- [[backend.app.ai.supervisor.AISupervisor.__init__|__init__]]
- [[backend.app.ai.supervisor.AISupervisor._pull_owns_state|_pull_owns_state]]
- [[backend.app.ai.supervisor.AISupervisor._run_pull|_run_pull]]
- [[backend.app.ai.supervisor.AISupervisor._run_pull.check_space|check_space]]
- [[backend.app.ai.supervisor.AISupervisor._run_pull.on_progress|on_progress]]
- [[backend.app.ai.supervisor.AISupervisor._set_state|_set_state]]
- [[backend.app.ai.supervisor.AISupervisor._smoke_test|_smoke_test]]
- [[backend.app.ai.supervisor.AISupervisor._tags|_tags]]
- [[backend.app.ai.supervisor.AISupervisor._try_auto_start|_try_auto_start]]
- [[backend.app.ai.supervisor.AISupervisor.cancel_pull|cancel_pull]]
- [[backend.app.ai.supervisor.AISupervisor.next_backoff_seconds|next_backoff_seconds]]
- [[backend.app.ai.supervisor.AISupervisor.on_analysis_failure|on_analysis_failure]]
- [[backend.app.ai.supervisor.AISupervisor.payload|payload]]
- [[backend.app.ai.supervisor.AISupervisor.pull_payload|pull_payload]]
- [[backend.app.ai.supervisor.AISupervisor.pulling|pulling]]
- [[backend.app.ai.supervisor.AISupervisor.queue_paused|queue_paused]]
- [[backend.app.ai.supervisor.AISupervisor.refresh|refresh]]
- [[backend.app.ai.supervisor.AISupervisor.reset_backoff|reset_backoff]]
- [[backend.app.ai.supervisor.AISupervisor.set_model|set_model]]
- [[backend.app.ai.supervisor.AISupervisor.start_pull|start_pull]]
- [[backend.app.ai.supervisor.AISupervisor.subscribe|subscribe]]
- [[backend.app.ai.supervisor.AISupervisor.wait_and_recheck|wait_and_recheck]]
- [[backend.app.ai.supervisor.find_ollama_executable|find_ollama_executable]]

## Constants

- `_AUTOSTART_POLL_SECONDS`
- `_BACKOFF_SCHEDULE`
- `_PAUSED_STATES`
- `_SMOKE_PROMPT`

---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.tests.test_model_supervisor
source: backend/tests/test_model_supervisor.py
status: active
tags: [module, backend]
---

# backend.tests.test_model_supervisor

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/tests/test_model_supervisor.py`

## Imports

- `AIState` ← `backend.app.ai.supervisor.AIState`
- `AISupervisor` ← `backend.app.ai.supervisor.AISupervisor`
- `OllamaInsufficientSpace` ← `backend.app.ai.ollama_client.OllamaInsufficientSpace`
- `OllamaPullFailed` ← `backend.app.ai.ollama_client.OllamaPullFailed`
- `PullProgress` ← `backend.app.ai.ollama_client.PullProgress`
- `asyncio` ← `asyncio`
- `pytest` ← `pytest`

## Classes

- [[backend.tests.test_model_supervisor.FakePullClient|FakePullClient]]

## Functions

- [[backend.tests.test_model_supervisor.FakePullClient.__init__|__init__]]
- [[backend.tests.test_model_supervisor.FakePullClient.generate|generate]]
- [[backend.tests.test_model_supervisor.FakePullClient.health|health]]
- [[backend.tests.test_model_supervisor.FakePullClient.list_models|list_models]]
- [[backend.tests.test_model_supervisor.FakePullClient.model_size|model_size]]
- [[backend.tests.test_model_supervisor.FakePullClient.pull_model|pull_model]]
- [[backend.tests.test_model_supervisor._start|_start]]
- [[backend.tests.test_model_supervisor.make_supervisor|make_supervisor]]
- [[backend.tests.test_model_supervisor.test_a_superseded_pull_cannot_overwrite_newer_state.run|run]]
- [[backend.tests.test_model_supervisor.test_analysis_failure_does_not_clobber_an_active_download.run|run]]
- [[backend.tests.test_model_supervisor.test_cancel_clears_progress_and_does_not_leave_a_stale_download_state.run|run]]
- [[backend.tests.test_model_supervisor.test_cancel_is_idempotent.run|run]]
- [[backend.tests.test_model_supervisor.test_insufficient_space_fails_the_pull_with_a_specific_code.run|run]]
- [[backend.tests.test_model_supervisor.test_pull_failure_is_reported_as_model_failed.run|run]]
- [[backend.tests.test_model_supervisor.test_pull_payload_formats_bytes_honestly.run|run]]
- [[backend.tests.test_model_supervisor.test_pull_payload_reports_null_fraction_until_a_total_is_announced.run|run]]
- [[backend.tests.test_model_supervisor.test_queue_is_paused_while_downloading_and_after_failure.run|run]]
- [[backend.tests.test_model_supervisor.test_queue_is_paused_while_downloading_and_after_failure.run2|run2]]
- [[backend.tests.test_model_supervisor.test_refresh_does_not_clobber_an_active_download.run|run]]
- [[backend.tests.test_model_supervisor.test_second_start_while_downloading_is_idempotent.run|run]]
- [[backend.tests.test_model_supervisor.test_set_model_refuses_while_a_download_is_running.run|run]]
- [[backend.tests.test_model_supervisor.test_start_pull_enters_downloading_and_publishes_real_bytes.run|run]]
- [[backend.tests.test_model_supervisor.test_successful_pull_runs_the_readiness_check_before_ready.run|run]]
- [[backend.tests.test_model_supervisor.test_unreachable_server_is_reported_before_a_pull_starts.run|run]]

## Tests

- [[backend.tests.test_model_supervisor.test_a_superseded_pull_cannot_overwrite_newer_state|test_a_superseded_pull_cannot_overwrite_newer_state]]
- [[backend.tests.test_model_supervisor.test_analysis_failure_does_not_clobber_an_active_download|test_analysis_failure_does_not_clobber_an_active_download]]
- [[backend.tests.test_model_supervisor.test_cancel_clears_progress_and_does_not_leave_a_stale_download_state|test_cancel_clears_progress_and_does_not_leave_a_stale_download_state]]
- [[backend.tests.test_model_supervisor.test_cancel_is_idempotent|test_cancel_is_idempotent]]
- [[backend.tests.test_model_supervisor.test_insufficient_space_fails_the_pull_with_a_specific_code|test_insufficient_space_fails_the_pull_with_a_specific_code]]
- [[backend.tests.test_model_supervisor.test_pull_failure_is_reported_as_model_failed|test_pull_failure_is_reported_as_model_failed]]
- [[backend.tests.test_model_supervisor.test_pull_payload_formats_bytes_honestly|test_pull_payload_formats_bytes_honestly]]
- [[backend.tests.test_model_supervisor.test_pull_payload_is_none_before_any_pull|test_pull_payload_is_none_before_any_pull]]
- [[backend.tests.test_model_supervisor.test_pull_payload_reports_null_fraction_until_a_total_is_announced|test_pull_payload_reports_null_fraction_until_a_total_is_announced]]
- [[backend.tests.test_model_supervisor.test_queue_is_paused_while_downloading_and_after_failure|test_queue_is_paused_while_downloading_and_after_failure]]
- [[backend.tests.test_model_supervisor.test_refresh_does_not_clobber_an_active_download|test_refresh_does_not_clobber_an_active_download]]
- [[backend.tests.test_model_supervisor.test_second_start_while_downloading_is_idempotent|test_second_start_while_downloading_is_idempotent]]
- [[backend.tests.test_model_supervisor.test_set_model_applies_when_idle|test_set_model_applies_when_idle]]
- [[backend.tests.test_model_supervisor.test_set_model_refuses_while_a_download_is_running|test_set_model_refuses_while_a_download_is_running]]
- [[backend.tests.test_model_supervisor.test_set_model_rejects_an_empty_name|test_set_model_rejects_an_empty_name]]
- [[backend.tests.test_model_supervisor.test_start_pull_enters_downloading_and_publishes_real_bytes|test_start_pull_enters_downloading_and_publishes_real_bytes]]
- [[backend.tests.test_model_supervisor.test_successful_pull_runs_the_readiness_check_before_ready|test_successful_pull_runs_the_readiness_check_before_ready]]
- [[backend.tests.test_model_supervisor.test_the_only_resource_constant_is_the_documented_ram_floor|test_the_only_resource_constant_is_the_documented_ram_floor]]
- [[backend.tests.test_model_supervisor.test_unreachable_server_is_reported_before_a_pull_starts|test_unreachable_server_is_reported_before_a_pull_starts]]

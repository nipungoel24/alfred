---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.tests.test_model_endpoints
source: backend/tests/test_model_endpoints.py
status: active
tags: [module, backend]
---

# backend.tests.test_model_endpoints

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/tests/test_model_endpoints.py`

## Imports

- `AIState` ← `backend.app.ai.supervisor.AIState`
- `AISupervisor` ← `backend.app.ai.supervisor.AISupervisor`
- `FakePullClient` ← `backend.tests.test_model_supervisor.FakePullClient`
- `Repository` ← `backend.app.db.repositories.Repository`
- `TestClient` ← `fastapi.testclient.TestClient`
- `main_mod` ← `backend.app.main`
- `pytest` ← `pytest`
- `time` ← `time`

## Functions

- [[backend.tests.test_model_endpoints._await_pull|_await_pull]]
- [[backend.tests.test_model_endpoints._state|_state]]
- [[backend.tests.test_model_endpoints._wire|_wire]]
- [[backend.tests.test_model_endpoints.client|client]]
- [[backend.tests.test_model_endpoints.client._noop|_noop]]
- [[backend.tests.test_model_endpoints.oauth_states|oauth_states]]

## Tests

- [[backend.tests.test_model_endpoints.test_a_denied_callback_releases_its_state_immediately|test_a_denied_callback_releases_its_state_immediately]]
- [[backend.tests.test_model_endpoints.test_a_pull_that_will_not_fit_the_disk_fails_with_a_real_shortfall|test_a_pull_that_will_not_fit_the_disk_fails_with_a_real_shortfall]]
- [[backend.tests.test_model_endpoints.test_an_abandoned_state_is_purged_once_the_ttl_passes|test_an_abandoned_state_is_purged_once_the_ttl_passes]]
- [[backend.tests.test_model_endpoints.test_an_expired_state_is_rejected_even_before_a_purge_runs|test_an_expired_state_is_rejected_even_before_a_purge_runs]]
- [[backend.tests.test_model_endpoints.test_cancelling_a_download_is_idempotent|test_cancelling_a_download_is_idempotent]]
- [[backend.tests.test_model_endpoints.test_cap_eviction_drops_the_oldest_not_an_arbitrary_flow|test_cap_eviction_drops_the_oldest_not_an_arbitrary_flow]]
- [[backend.tests.test_model_endpoints.test_model_status_populates_the_preflight_from_this_machine|test_model_status_populates_the_preflight_from_this_machine]]
- [[backend.tests.test_model_endpoints.test_model_status_reports_a_real_size_and_a_real_disk_free|test_model_status_reports_a_real_size_and_a_real_disk_free]]
- [[backend.tests.test_model_endpoints.test_model_status_survives_an_offline_ollama|test_model_status_survives_an_offline_ollama]]
- [[backend.tests.test_model_endpoints.test_pull_is_idempotent_while_running|test_pull_is_idempotent_while_running]]
- [[backend.tests.test_model_endpoints.test_pull_returns_live_progress_on_the_status_endpoint|test_pull_returns_live_progress_on_the_status_endpoint]]
- [[backend.tests.test_model_endpoints.test_pulling_a_new_model_synchronizes_settings_and_service|test_pulling_a_new_model_synchronizes_settings_and_service]]
- [[backend.tests.test_model_endpoints.test_purging_keeps_concurrent_recent_flows_alive|test_purging_keeps_concurrent_recent_flows_alive]]
- [[backend.tests.test_model_endpoints.test_selecting_a_model_re_runs_the_readiness_check|test_selecting_a_model_re_runs_the_readiness_check]]
- [[backend.tests.test_model_endpoints.test_selecting_an_empty_model_is_rejected|test_selecting_an_empty_model_is_rejected]]
- [[backend.tests.test_model_endpoints.test_the_model_cannot_be_changed_while_a_download_runs|test_the_model_cannot_be_changed_while_a_download_runs]]
- [[backend.tests.test_model_endpoints.test_the_state_dict_never_exceeds_its_cap|test_the_state_dict_never_exceeds_its_cap]]

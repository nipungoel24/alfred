---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.resources
qualified_name: backend.app.ai.resources.check_for_model_download
source: backend/app/ai/resources.py
line: 134
status: active
tags: [ai, function]
---

# check_for_model_download

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Decide whether a model download may start on this machine.

## Location

`backend/app/ai/resources.py:134`

## Signature

```python
(required_bytes: int | None) -> ResourceCheck
```

## Parameters

- `required_bytes` (`int | None`)

## Returns

`ResourceCheck`

## Called By

- [[backend.app.ai.supervisor.AISupervisor._run_pull|_run_pull]]
- [[backend.app.ai.supervisor.AISupervisor._run_pull.check_space|check_space]]
- [[backend.app.main.ai_model|ai_model]]
- [[backend.tests.test_model_pull.test_insufficient_disk_space_blocks_with_an_actionable_message|test_insufficient_disk_space_blocks_with_an_actionable_message]]
- [[backend.tests.test_model_pull.test_low_ram_blocks_before_a_download_starts|test_low_ram_blocks_before_a_download_starts]]
- [[backend.tests.test_model_pull.test_sufficient_space_and_ram_do_not_block|test_sufficient_space_and_ram_do_not_block]]
- [[backend.tests.test_model_pull.test_the_preflight_runs_against_this_machine|test_the_preflight_runs_against_this_machine]]
- [[backend.tests.test_model_pull.test_unknown_required_size_does_not_block|test_unknown_required_size_does_not_block]]
- [[backend.tests.test_model_pull.test_unreadable_disk_is_blocking|test_unreadable_disk_is_blocking]]
- [[backend.tests.test_model_pull.test_unreadable_ram_is_reported_as_uncertain_not_as_failure|test_unreadable_ram_is_reported_as_uncertain_not_as_failure]]

## Side Effects

- none statically observed

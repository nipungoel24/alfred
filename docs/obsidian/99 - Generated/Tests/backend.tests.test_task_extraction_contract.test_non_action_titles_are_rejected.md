---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_task_extraction_contract
qualified_name: backend.tests.test_task_extraction_contract.test_non_action_titles_are_rejected
source: backend/tests/test_task_extraction_contract.py
line: 223
status: active
tags: [test, function, test]
---

# test_non_action_titles_are_rejected

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_non_action_titles_are_rejected` in `backend/tests/test_task_extraction_contract.py`.

## Location

`backend/tests/test_task_extraction_contract.py:223`

## Signature

```python
(bad_title)
```

## Parameters

- `bad_title`

## Calls

- [[backend.app.schemas.Deadline|Deadline]] (calls)
- `is_temporal_only` (`backend.app.services.due_dates.is_temporal_only`, calls-inferred)
- [[backend.app.services.task_derivation.derive_tasks|derive_tasks]] (calls)

## Side Effects

- none statically observed

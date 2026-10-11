---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.resources
qualified_name: backend.app.ai.resources.disk_status
source: backend/app/ai/resources.py
line: 55
status: active
tags: [ai, function]
---

# disk_status

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Read real free/total bytes for the filesystem holding `path`.

## Location

`backend/app/ai/resources.py:55`

## Signature

```python
(path: str | None = None) -> DiskStatus
```

## Parameters

- `path` (`str | None`)

## Returns

`DiskStatus`

## Calls

- `dirname` (`os.path.dirname`, calls-inferred)
- `exists` (`os.path.exists`, calls-inferred)
- `disk_usage` (`shutil.disk_usage`, calls-inferred)

## Called By

- [[backend.tests.test_model_pull.test_disk_status_reports_real_free_space|test_disk_status_reports_real_free_space]]
- [[backend.tests.test_model_pull.test_disk_status_walks_up_to_an_existing_ancestor|test_disk_status_walks_up_to_an_existing_ancestor]]
- [[backend.tests.test_model_pull.test_the_preflight_runs_against_this_machine|test_the_preflight_runs_against_this_machine]]

## Side Effects

- none statically observed

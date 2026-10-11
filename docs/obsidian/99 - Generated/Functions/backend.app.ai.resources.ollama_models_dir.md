---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.resources
qualified_name: backend.app.ai.resources.ollama_models_dir
source: backend/app/ai/resources.py
line: 21
status: active
tags: [ai, function]
---

# ollama_models_dir

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

The directory Ollama stores model layers in, on this machine.

## Location

`backend/app/ai/resources.py:21`

## Signature

```python
() -> str
```

## Returns

`str`

## Calls

- `get` (`os.environ.get`, calls-inferred)
- `expanduser` (`os.path.expanduser`, calls-inferred)
- `join` (`os.path.join`, calls-inferred)

## Called By

- [[backend.tests.test_model_pull.test_disk_status_walks_up_to_an_existing_ancestor|test_disk_status_walks_up_to_an_existing_ancestor]]
- [[backend.tests.test_model_pull.test_models_dir_is_a_real_path_on_this_machine|test_models_dir_is_a_real_path_on_this_machine]]

## Side Effects

- none statically observed

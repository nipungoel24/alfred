---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_ai_supervisor
qualified_name: backend.tests.test_ai_supervisor.test_failure_classification
source: backend/tests/test_ai_supervisor.py
line: 104
status: active
tags: [test, function, test]
---

# test_failure_classification

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Mid-analysis failures map to the right states.

## Location

`backend/tests/test_ai_supervisor.py:104`

## Signature

```python
(monkeypatch)
```

## Parameters

- `monkeypatch`

## Calls

- [[backend.app.ai.ollama_client.OllamaModelMissing|OllamaModelMissing]] (calls)
- [[backend.app.ai.ollama_client.OllamaTimeout|OllamaTimeout]] (calls)
- [[backend.app.ai.ollama_client.OllamaUnavailable|OllamaUnavailable]] (calls)

## Side Effects

- network (HTTP)

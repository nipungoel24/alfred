---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_ai_supervisor.FakeClient
qualified_name: backend.tests.test_ai_supervisor.FakeClient.generate
source: backend/tests/test_ai_supervisor.py
line: 33
status: active
tags: [test, function]
---

# generate

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `generate` in `backend/tests/test_ai_supervisor.py`.

## Location

`backend/tests/test_ai_supervisor.py:33`

## Signature

```python
(self, model, prompt, schema = None, temperature = 0.0)
```

## Parameters

- `self`
- `model`
- `prompt`
- `schema`
- `temperature`

## Calls

- [[backend.app.ai.ollama_client.OllamaTimeout|OllamaTimeout]] (calls)
- [[backend.app.ai.ollama_client.OllamaUnavailable|OllamaUnavailable]] (calls)

## Side Effects

- async I/O; network (HTTP)

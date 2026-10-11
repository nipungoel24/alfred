---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_model_supervisor.FakePullClient
qualified_name: backend.tests.test_model_supervisor.FakePullClient.pull_model
source: backend/tests/test_model_supervisor.py
line: 79
status: active
tags: [test, function]
---

# pull_model

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `pull_model` in `backend/tests/test_model_supervisor.py`.

## Location

`backend/tests/test_model_supervisor.py:79`

## Signature

```python
(self, model, on_progress = None, check_space = None)
```

## Parameters

- `self`
- `model`
- `on_progress`
- `check_space`

## Calls

- `sleep` (`asyncio.sleep`, calls-inferred)
- [[backend.app.ai.ollama_client.OllamaInsufficientSpace|OllamaInsufficientSpace]] (calls)
- [[backend.app.ai.ollama_client.OllamaPullFailed|OllamaPullFailed]] (calls)
- [[backend.app.ai.ollama_client.PullProgress|PullProgress]] (calls)

## Side Effects

- async I/O; network (HTTP)

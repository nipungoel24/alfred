---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_ollama_mock
qualified_name: backend.tests.test_ollama_mock.test_ollama_client_http_error
source: backend/tests/test_ollama_mock.py
line: 57
status: active
tags: [test, function, test]
---

# test_ollama_client_http_error

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_ollama_client_http_error` in `backend/tests/test_ollama_mock.py`.

## Location

`backend/tests/test_ollama_mock.py:57`

## Signature

```python
()
```

## Calls

- `run` (`asyncio.run`, calls-inferred)
- [[backend.app.ai.ollama_client.OllamaClient|OllamaClient]] (calls)
- `HTTPError` (`httpx.HTTPError`, calls-inferred)
- `raises` (`pytest.raises`, calls-inferred)
- `AsyncMock` (`unittest.mock.AsyncMock`, calls-inferred)

## Side Effects

- network (HTTP)

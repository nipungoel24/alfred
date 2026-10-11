---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.ollama_client
qualified_name: backend.app.ai.ollama_client._parse_record
source: backend/app/ai/ollama_client.py
line: 95
status: active
tags: [ai, function]
---

# _parse_record

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `_parse_record` in `backend/app/ai/ollama_client.py`.

## Location

`backend/app/ai/ollama_client.py:95`

## Signature

```python
(line: str, decoder: NdjsonStreamDecoder | None = None) -> dict | None
```

## Parameters

- `line` (`str`)
- `decoder` (`NdjsonStreamDecoder | None`)

## Returns

`dict | None`

## Calls

- `loads` (`json.loads`, calls-inferred)

## Side Effects

- none statically observed

---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.ollama_client.NdjsonStreamDecoder
qualified_name: backend.app.ai.ollama_client.NdjsonStreamDecoder.feed
source: backend/app/ai/ollama_client.py
line: 67
status: active
tags: [ai, function]
---

# feed

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Decode one network chunk; return every record it completed.

## Location

`backend/app/ai/ollama_client.py:67`

## Signature

```python
(self, chunk: bytes) -> list[dict]
```

## Parameters

- `self`
- `chunk` (`bytes`)

## Returns

`list[dict]`

## Side Effects

- none statically observed

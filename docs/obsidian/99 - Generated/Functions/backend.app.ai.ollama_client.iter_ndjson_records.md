---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.ollama_client
qualified_name: backend.app.ai.ollama_client.iter_ndjson_records
source: backend/app/ai/ollama_client.py
line: 114
status: active
tags: [ai, function]
---

# iter_ndjson_records

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Convenience wrapper over `NdjsonStreamDecoder` for plain byte chunks.

## Location

`backend/app/ai/ollama_client.py:114`

## Signature

```python
(chunks: Iterable[bytes]) -> Iterator[dict]
```

## Parameters

- `chunks` (`Iterable[bytes]`)

## Returns

`Iterator[dict]`

## Called By

- [[backend.tests.test_model_pull.test_blank_lines_are_ignored|test_blank_lines_are_ignored]]
- [[backend.tests.test_model_pull.test_malformed_record_is_dropped_without_losing_neighbours|test_malformed_record_is_dropped_without_losing_neighbours]]
- [[backend.tests.test_model_pull.test_multi_byte_utf8_split_across_chunks|test_multi_byte_utf8_split_across_chunks]]
- [[backend.tests.test_model_pull.test_non_object_record_is_dropped|test_non_object_record_is_dropped]]
- [[backend.tests.test_model_pull.test_records_split_across_network_chunks_are_reassembled|test_records_split_across_network_chunks_are_reassembled]]

## Side Effects

- none statically observed

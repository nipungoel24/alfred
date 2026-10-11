---
type: class
generated: true
language: python
layer: ai
module: backend.app.ai.ollama_client
qualified_name: backend.app.ai.ollama_client.NdjsonStreamDecoder
source: backend/app/ai/ollama_client.py
line: 47
status: active
tags: [ai, class]
---

# NdjsonStreamDecoder

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Incremental decoder for a newline-delimited JSON byte stream.

## Location

`backend/app/ai/ollama_client.py:47`

## Called By

- [[backend.tests.test_model_pull.test_incomplete_final_record_is_not_emitted_until_flush|test_incomplete_final_record_is_not_emitted_until_flush]]
- [[backend.tests.test_model_pull.test_incomplete_final_record_without_newline_is_emitted_by_flush|test_incomplete_final_record_without_newline_is_emitted_by_flush]]
- [[backend.tests.test_model_pull.test_malformed_record_is_dropped_without_losing_neighbours|test_malformed_record_is_dropped_without_losing_neighbours]]
- [[backend.tests.test_model_pull.test_unparseable_incomplete_tail_is_dropped_not_invented|test_unparseable_incomplete_tail_is_dropped_not_invented]]

## Side Effects

- none statically observed

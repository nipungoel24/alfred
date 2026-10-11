---
type: class
generated: true
language: python
layer: ai
module: backend.app.ai.ollama_client
qualified_name: backend.app.ai.ollama_client.LayerProgressAggregator
source: backend/app/ai/ollama_client.py
line: 146
status: active
tags: [ai, class]
---

# LayerProgressAggregator

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Tracks per-layer byte counts without double-counting.

## Location

`backend/app/ai/ollama_client.py:146`

## Called By

- [[backend.tests.test_model_pull.test_layer_aggregation_handles_already_verified_resumed_layers|test_layer_aggregation_handles_already_verified_resumed_layers]]
- [[backend.tests.test_model_pull.test_multiple_layers_are_summed_once_each|test_multiple_layers_are_summed_once_each]]
- [[backend.tests.test_model_pull.test_repeated_updates_for_one_digest_do_not_double_count|test_repeated_updates_for_one_digest_do_not_double_count]]
- [[backend.tests.test_model_pull.test_status_is_retained_across_layer_records|test_status_is_retained_across_layer_records]]
- [[backend.tests.test_model_pull.test_status_records_without_bytes_do_not_invent_a_total|test_status_records_without_bytes_do_not_invent_a_total]]

## Side Effects

- none statically observed

---
type: class
generated: true
language: python
layer: ai
module: backend.app.ai.ollama_client
qualified_name: backend.app.ai.ollama_client.OllamaClient
source: backend/app/ai/ollama_client.py
line: 206
status: active
tags: [ai, class]
---

# OllamaClient

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Async HTTP client for Ollama's /api/generate endpoint.

## Location

`backend/app/ai/ollama_client.py:206`

## Called By

- [[backend.tests.test_extended.test_model_unavailable|test_model_unavailable]]
- [[backend.tests.test_extended.test_ollama_empty_response|test_ollama_empty_response]]
- [[backend.tests.test_model_pull._client_for|_client_for]]
- [[backend.tests.test_model_pull.test_cancelling_the_pull_task_closes_the_stream|test_cancelling_the_pull_task_closes_the_stream]]
- [[backend.tests.test_model_pull.test_list_models_reports_names_and_sizes_without_invention|test_list_models_reports_names_and_sizes_without_invention]]
- [[backend.tests.test_model_pull.test_model_size_uses_the_real_reported_size|test_model_size_uses_the_real_reported_size]]
- [[backend.tests.test_model_pull.test_pull_splits_records_across_chunks_while_streaming|test_pull_splits_records_across_chunks_while_streaming]]
- [[backend.tests.test_ollama_mock.test_ai_service_analyze_email_success|test_ai_service_analyze_email_success]]
- [[backend.tests.test_ollama_mock.test_ollama_client_empty_response|test_ollama_client_empty_response]]
- [[backend.tests.test_ollama_mock.test_ollama_client_http_error|test_ollama_client_http_error]]
- [[backend.tests.test_ollama_mock.test_ollama_client_sends_correct_payload|test_ollama_client_sends_correct_payload]]

## Side Effects

- none statically observed

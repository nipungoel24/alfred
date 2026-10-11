---
type: class
generated: true
language: python
layer: ai
module: backend.app.ai.ollama_client
qualified_name: backend.app.ai.ollama_client.OllamaInsufficientSpace
source: backend/app/ai/ollama_client.py
line: 35
status: active
tags: [ai, class]
---

# OllamaInsufficientSpace

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Free space ran out (or was already too low) for the announced download.

## Location

`backend/app/ai/ollama_client.py:35`

## Bases

- `Exception`

## Called By

- [[backend.app.ai.supervisor.AISupervisor._run_pull|_run_pull]]
- [[backend.app.ai.supervisor.AISupervisor._run_pull.check_space|check_space]]
- [[backend.tests.test_model_pull.test_space_check_aborts_the_download_before_it_fills_the_disk|test_space_check_aborts_the_download_before_it_fills_the_disk]]
- [[backend.tests.test_model_pull.test_space_check_aborts_the_download_before_it_fills_the_disk.check|check]]
- [[backend.tests.test_model_supervisor.FakePullClient.pull_model|pull_model]]

## Side Effects

- none statically observed

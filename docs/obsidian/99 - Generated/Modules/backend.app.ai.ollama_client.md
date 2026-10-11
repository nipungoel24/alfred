---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.app.ai.ollama_client
source: backend/app/ai/ollama_client.py
status: active
tags: [module, backend]
---

# backend.app.ai.ollama_client

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/app/ai/ollama_client.py`

## Imports

- `Callable` ← `typing.Callable`
- `Iterable` ← `typing.Iterable`
- `Iterator` ← `typing.Iterator`
- `codecs` ← `codecs`
- `dataclass` ← `dataclasses.dataclass`
- `httpx` ← `httpx`
- `json` ← `json`
- `logging` ← `logging`
- `re` ← `re`
- `time` ← `time`

## Classes

- [[backend.app.ai.ollama_client.InferenceMetrics|InferenceMetrics]]
- [[backend.app.ai.ollama_client.LayerProgressAggregator|LayerProgressAggregator]]
- [[backend.app.ai.ollama_client.NdjsonStreamDecoder|NdjsonStreamDecoder]]
- [[backend.app.ai.ollama_client.OllamaClient|OllamaClient]]
- [[backend.app.ai.ollama_client.OllamaInsufficientSpace|OllamaInsufficientSpace]]
- [[backend.app.ai.ollama_client.OllamaInvalidResponse|OllamaInvalidResponse]]
- [[backend.app.ai.ollama_client.OllamaModelMissing|OllamaModelMissing]]
- [[backend.app.ai.ollama_client.OllamaPullFailed|OllamaPullFailed]]
- [[backend.app.ai.ollama_client.OllamaTimeout|OllamaTimeout]]
- [[backend.app.ai.ollama_client.OllamaUnavailable|OllamaUnavailable]]
- [[backend.app.ai.ollama_client.PullProgress|PullProgress]]

## Functions

- [[backend.app.ai.ollama_client.InferenceMetrics.__init__|__init__]]
- [[backend.app.ai.ollama_client.LayerProgressAggregator.__init__|__init__]]
- [[backend.app.ai.ollama_client.LayerProgressAggregator.announced_total|announced_total]]
- [[backend.app.ai.ollama_client.LayerProgressAggregator.observe|observe]]
- [[backend.app.ai.ollama_client.NdjsonStreamDecoder.__init__|__init__]]
- [[backend.app.ai.ollama_client.NdjsonStreamDecoder._drain|_drain]]
- [[backend.app.ai.ollama_client.NdjsonStreamDecoder.feed|feed]]
- [[backend.app.ai.ollama_client.NdjsonStreamDecoder.flush|flush]]
- [[backend.app.ai.ollama_client.NdjsonStreamDecoder.malformed_count|malformed_count]]
- [[backend.app.ai.ollama_client.OllamaClient.__init__|__init__]]
- [[backend.app.ai.ollama_client.OllamaClient.generate|generate]]
- [[backend.app.ai.ollama_client.OllamaClient.health|health]]
- [[backend.app.ai.ollama_client.OllamaClient.list_models|list_models]]
- [[backend.app.ai.ollama_client.OllamaClient.model_size|model_size]]
- [[backend.app.ai.ollama_client.OllamaClient.preload_model|preload_model]]
- [[backend.app.ai.ollama_client.OllamaClient.pull_model|pull_model]]
- [[backend.app.ai.ollama_client.OllamaClient.pull_model.handle|handle]]
- [[backend.app.ai.ollama_client.OllamaInsufficientSpace.__init__|__init__]]
- [[backend.app.ai.ollama_client.PullProgress.fraction|fraction]]
- [[backend.app.ai.ollama_client._parse_record|_parse_record]]
- [[backend.app.ai.ollama_client.iter_ndjson_records|iter_ndjson_records]]

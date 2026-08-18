---
type: architecture
layer: ai
status: active
tags:
  - ai
---

# Ollama Integration

The transport layer between Alfred and the local model — [[backend.app.ai.ollama_client.OllamaClient|OllamaClient]].

## Request shape

- Endpoint: `{OLLAMA_BASE_URL}/api/generate` (default `http://127.0.0.1:11434`).
- Payload: `model`, `prompt`, `stream: false`, `think: false`, `keep_alive: 30m`, `options.temperature`, and — when structured output is required — `format: <JSON Schema>`.
- Preload: a keep-alive request warms the model at startup (`preload_model`, 180s timeout, non-fatal).

## Response handling

- Text comes from `response`; `<think>`/`<thinking>` tag leakage is stripped with a regex.
- Empty output on a structured call raises [[backend.app.ai.ollama_client.OllamaInvalidResponse]].
- Nanosecond durations → `InferenceMetrics` (ms) + token counts, recorded in [[inference_metrics]].

## Error taxonomy

| Class | Trigger | Worker treatment |
|---|---|---|
| [[backend.app.ai.ollama_client.OllamaUnavailable]] | connection/HTTP failure | retryable + backoff |
| [[backend.app.ai.ollama_client.OllamaTimeout]] | 120s timeout | retryable + backoff |
| [[backend.app.ai.ollama_client.OllamaInvalidResponse]] | unparseable/empty structured output | failed (per job) |
| [[backend.app.ai.ollama_client.OllamaModelMissing]] | 404 model | failed (per job) |

HTTP handlers map these to 503/504/502 responses for the API ([[API Overview]]).

## Related

- [[Model Configuration]]
- [[AI Failure Handling]]
- [[Structured Output]]

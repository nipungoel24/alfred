---
type: data-flow
layer: ai
status: active
tags:
  - system
  - ai
  - critical-path
---

# Email Analysis Flow

One email through the local AI, from queue to cached verdict.

```mermaid
sequenceDiagram
    participant W as Analysis Worker
    participant R as Repository
    participant AS as AIService
    participant OC as OllamaClient
    participant O as Ollama (qwen3:4b)

    W->>R: next_job('analyze_email') by priority
    W->>R: email_eligibility(id) — guard
    alt excluded (became spam/archived since enqueue)
        W->>R: job cancelled
    else eligible
        W->>R: cached_analysis(id, fingerprint)?
        alt hit
            W->>W: derive tasks from cache; job succeeded
        else miss
            W->>AS: analyze_email(email)
            AS->>AS: _prepare_body (truncate 2000, strip quotes/base64/urls)
            AS->>OC: generate(model, prompt, EmailAnalysis JSON schema)
            OC->>O: POST /api/generate {format: schema, stream:false}
            O-->>OC: {response, timings}
            OC-->>AS: (clean_text, InferenceMetrics)
            AS-->>W: EmailAnalysis (schema-validated)
            W->>R: save_analysis + inference metrics
            W->>W: _derive_and_save_tasks (eligibility re-checked)
        end
    end
```

## Where the intelligence comes from

- [[backend.app.ai.service.AIService.analyze_email]] builds the prompt from sender/subject/recipients + sanitized body ([[Prompt Architecture]]).
- [[backend.app.ai.ollama_client.OllamaClient.generate]] enforces `stream=false`, `think=false`, and passes the Pydantic JSON Schema as `format` ([[Structured Output]]).
- Thinking-tag leakage is stripped; empty structured output raises [[backend.app.ai.ollama_client.OllamaInvalidResponse]].

## Ordering

Jobs carry policy-derived priorities ([[backend.app.mail.eligibility.MailEligibilityPolicy.analysis_queue_priority|analysis_queue_priority]]): Gmail-IMPORTANT and unread Primary first, Promotions last; lazy categories aren't scheduled at all unless Gmail IMPORTANT or explicit user action.

## Failure handling

Ollama down → retryable with backoff and a pause after consecutive failures; invalid response/model missing → terminal failure with error codes; everything broadcast over SSE. See [[AI Failure Handling]].

## Related

- [[Background Analysis Job Flow]]
- [[Task Derivation Flow]]
- [[AI Caching]]
- [[Email Analysis Flow#Tests]] — golden corpus: [[Golden Email Corpus]]

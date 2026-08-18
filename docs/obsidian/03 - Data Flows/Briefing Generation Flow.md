---
type: data-flow
layer: ai
status: active
tags:
  - system
  - ai
---

# Briefing Generation Flow

The morning executive summary, with model output never trusted for arithmetic.

```mermaid
sequenceDiagram
    participant F as Frontend (OverviewPage)
    participant BE as FastAPI
    participant R as Repository
    participant AS as AIService
    participant O as Ollama

    F->>BE: GET /api/briefing
    BE->>R: _briefing_eligible_emails()
    Note over R: active inbox + policy filter (no spam/trash; promo/social only with strong signals)
    R-->>BE: eligible emails + cached analyses
    BE->>BE: briefing_fingerprint(analyses)
    BE->>R: cached_briefing?
    alt hit
        R-->>BE: cached InboxBriefing
    else miss
        BE->>AS: generate_inbox_briefing(emails)
        AS->>O: compact analyses + schema
        O-->>AS: InboxBriefing JSON
        AS->>AS: recompute counts locally; sanitize meta-language/ISO timestamps
        BE->>R: save_briefing(fingerprint)
    end
    BE-->>F: briefing
```

## Correctness guards

- **One authoritative candidate set** — `_briefing_eligible_emails` in [[backend.app.main]] applies [[backend.app.mail.eligibility.MailEligibilityPolicy.should_include_in_briefing|should_include_in_briefing]]; a spam-labeled message with an old analysis can never re-enter via cache (fingerprint covers only eligible analyses).
- **Counts are local** — `total/urgent/high/needs_reply/deadline` are computed from the eligible set, overriding the model ([[backend.app.ai.service.AIService.generate_inbox_briefing]]).
- **Meta-language guard** — if the small model describes its input ("the user has provided…") or leaks ISO timestamps, the executive summary is replaced with a factual fallback (`_owner_facing_briefing_summary`).
- **Cache key** — [[backend.app.mail.briefing_fingerprint.briefing_fingerprint]] hashes the *analyses* of the eligible set + schema version + model; new mail or new analyses invalidate it.

## Endpoints

- [[GET --api-briefing]] — cached read.
- [[POST --api-briefing-generate]] — forced regeneration.

## Related

- [[AI Caching]]
- [[Prompt Architecture]]
- [[frontend.src.features.overview.OverviewPage.OverviewPage|OverviewPage]]
- [[Deadline Extraction Flow]]

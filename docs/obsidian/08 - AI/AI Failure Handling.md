---
type: architecture
layer: ai
status: active
tags:
  - ai
---

# AI Failure Handling

What happens when the model is down, slow, or wrong — end to end.

## Worker level ([[backend.app.main._analysis_worker]])

| Failure | Job outcome | System effect |
|---|---|---|
| Ollama unreachable / timeout | `retryable_failed` + attempts | after 5 consecutive → 30s pause, then retry |
| Invalid structured output | `failed` (no point retrying same prompt) | job counted, email stays unanalyzed until content/schema changes |
| Model missing (404) | `failed` | same |
| Email became ineligible mid-queue | `cancelled` | SSE `analysis_cancelled` |

## API level

[[GET --health]] reports `ai: ready | unavailable`; typed exceptions map to 502/503/504 ([[API Overview]]). The frontend header chip flips to "AI Offline" with an explanatory tooltip.

## UI level

- Briefing/draft failures → scoped banners ("Is the local AI runtime running?"), the rest of the app keeps working.
- Pending analysis shows the calm "analysis pending" state in the [[frontend.src.intelligence.IntelligencePanel.IntelligencePanel|IntelligencePanel]] instead of errors.
- The progress pill reports last-error context and disappears when the queue drains.

## Retry budget

`attempts < max_attempts` on retryable failures; backfill uses exponential backoff with a 5-minute cap ([[All Mail Backfill Flow]]); analysis uses the 30s pause after consecutive failures.

## Related

- [[Ollama Integration]]
- [[Background Analysis Job Flow]]
- [[Project Status]]

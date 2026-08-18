---
type: architecture
layer: test
status: active
tags:
  - test
---

# Backend Tests

Pytest suites under `backend/tests/` (+ shared helpers in `tests/`). Run: `py -m pytest backend/tests -q`.

| File | Focus |
|---|---|
| [[backend.tests.test_core]] | Core persistence: email/analysis/briefing CRUD round-trips |
| [[backend.tests.test_extended]] | API flows (import/list/analyze/draft/briefing) + malicious HTML normalization |
| [[backend.tests.test_gmail_mock]] | OAuth URL, token exchange, initial/incremental sync, history expiry recovery, load-older, HTML sanitization |
| [[backend.tests.test_eligibility]] | Category corpus, transitions (spam↔inbox, archive), briefing policy, label-history updates, API exclusion |
| [[backend.tests.test_allmail]] | Scopes, kind filters, archived/sent visibility, backfill pages/resume/dupes |
| [[backend.tests.test_backfill_jobs]] | Durable job rows, not_before scheduling, backoff/promotion, priority below analysis, re-arm |
| [[backend.tests.test_ollama_mock]] | OllamaClient error taxonomy + metrics parsing |
| [[backend.tests.test_golden_corpus]] | Structured-output contract on fixed emails ([[Golden Email Corpus]]) |
| [[backend.tests.test_task_derivation]] | Noise/ownership/confidence/dedupe gates |
| [[backend.tests.test_task_migration]] | Migration reconciliation + idempotency |

Generated per-test notes live in `99 - Generated/Tests`.

## Related

- [[Testing Strategy]]
- [[Test Coverage Map]]

---
type: architecture
layer: test
status: active
tags:
  - test
  - architecture
---

# Testing Strategy

Alfred's testing pyramid is inverted toward its risks: policy rules, mail flows, and data safety get the most automated weight.

| Layer | Suite | What it proves |
|---|---|---|
| Backend unit | `backend/tests/*` (pytest) | OAuth URL/flow, sync state machine, normalization, HTML sanitization |
| Policy corpus | [[backend.tests.test_eligibility]] | mailbox states, category mapping, transitions, briefing/task exclusions |
| All Mail | [[backend.tests.test_allmail]], [[backend.tests.test_backfill_jobs]] | scopes, kind filters, backfill pagination/resume/backoff/dupes |
| AI | [[backend.tests.test_ollama_mock]], [[Golden Email Corpus]] | structured-output contract, prompt robustness, schema validation |
| Task derivation | [[backend.tests.test_task_derivation]] | noise/ownership/dedupe/confidence gates |
| Migration | [[backend.tests.test_task_migration]] | idempotency, user-state preservation |
| API integration | [[backend.tests.test_extended]] | import → list → analyze → draft → briefing flows |
| Frontend | Vitest (`frontend/src/**/*.test.tsx`, `frontend/tests/`) | theme, workspace switching, categories, selection/intelligence, Later, keyboard |
| Real Gmail | Manual acceptance (no mailbox reset) | live sync, label transitions, backfill restart-resume — see [[Gmail E2E Testing]] |
| Docs tooling | `tools/docs/tests` | generator determinism, route/table detection, staleness check |

## Principles

- Mock at the network boundary (httpx patches), never re-implement providers.
- Golden corpus is fixed-email data — the AI contract is tested without Ollama flakiness.
- Migration tests assert *user state preservation*, not just row counts.
- Frontend tests assert behavior through roles/aria, not implementation.

## Related

- [[Test Coverage Map]]
- [[Backend Tests]]
- [[Frontend Tests]]

---
type: architecture
layer: backend
status: active
tags:
  - system
  - architecture
  - backend
---

# Backend Architecture

The FastAPI sidecar is a single-process, async application with **two in-process workers** and a shared SQLite repository. No Celery, no Redis, no extra services.

## Layers

| Layer | Modules | Responsibility |
|---|---|---|
| HTTP | [[backend.app.main]] | All routes, SSE hub, lifespan |
| Services | [[backend.app.ai.service]], [[backend.app.services.task_derivation]], [[backend.app.services.task_migration]] | AI orchestration + business rules |
| Mail | [[backend.app.mail.providers.gmail]], [[backend.app.mail.eligibility]], [[backend.app.mail.backfill]], [[backend.app.mail.fingerprint]], [[backend.app.mail.normalizer]] | Gmail client + mailbox policy |
| AI infra | [[backend.app.ai.ollama_client]] | Ollama HTTP + error classification |
| Data | [[backend.app.db.repositories]], [[backend.app.db.database]], [[backend.app.db.secure_store]] | SQLite access + DPAPI |
| Models | [[backend.app.schemas]] | Pydantic contracts shared with AI structured output |

## The two workers

Both live in `main.py` as `asyncio` loops polling the [[jobs]] table:

1. **Analysis worker** — [[backend.app.main._analysis_worker]]: picks the highest-priority `analyze_email` job, guards eligibility, calls [[backend.app.ai.service.AIService.analyze_email]], derives tasks, persists. Retry semantics for Ollama failures; pauses after consecutive failures.
2. **Backfill worker** — [[backend.app.main._backfill_worker]]: pages through archived/sent Gmail mail one bounded page at a time with `not_before` rate limiting; priority 5 (always below analysis). See [[All Mail Backfill Flow]].

## Dependency rules

- Routes never touch SQL directly; they use [[backend.app.db.repositories.Repository]].
- Mailbox policy lives **only** in [[backend.app.mail.eligibility.MailEligibilityPolicy]] — no scattered `if "SPAM" in labels`.
- Task creation lives **only** in [[backend.app.services.task_derivation.derive_tasks]] + [[backend.app.services.task_migration.TaskMigrationService]].
- Gmail wire details live **only** in [[backend.app.mail.providers.gmail.GmailProvider]].

## Startup & shutdown

[[backend.app.main.lifespan]]: preload model → rebuild tasks if derivation version changed → reset stuck jobs → resume backfill jobs → start both workers → spawn one-shot backfills (label backfill, estimate fetch). On shutdown: cancel workers, close SQLite. See [[Application Startup Flow]].

## Related

- [[Backend Code Map]]
- [[Backend Overview]]
- [[Entry Points]]

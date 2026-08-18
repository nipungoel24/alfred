---
type: architecture
layer: backend
status: active
tags:
  - backend
  - architecture
---

# Backend Overview

The FastAPI application in `backend/app`. Entry point: [[backend.app.main]] (module note: [[backend.app.main]]).

## Module map

| Module | Role |
|---|---|
| [[backend.app.main]] | Routes, SSE, both workers, lifespan |
| [[backend.app.config]] | `Settings` from environment ([[Environment Variables]]) |
| [[backend.app.schemas]] | Pydantic contracts (also the AI output schemas) |
| [[backend.app.db.database]] | Schema, indexes, migrations, transactions |
| [[backend.app.db.repositories]] | All SQLite access |
| [[backend.app.db.secure_store]] | DPAPI encrypt/decrypt |
| [[backend.app.mail.eligibility]] | Mailbox state, categories, pipeline policy |
| [[backend.app.mail.backfill]] | Typed backfill cursor model |
| [[backend.app.mail.fingerprint]] | Content fingerprint (analysis cache key) |
| [[backend.app.mail.briefing_fingerprint]] | Briefing cache key |
| [[backend.app.mail.normalizer]] | CSV import normalization (legacy ingest) |
| [[backend.app.mail.providers.gmail]] | Gmail API client ([[backend.app.mail.providers.gmail.GmailProvider|GmailProvider]]) |
| [[backend.app.ai.ollama_client]] | Ollama HTTP + error taxonomy |
| [[backend.app.ai.service]] | Prompts + orchestration ([[backend.app.ai.service.AIService|AIService]]) |
| [[backend.app.services.task_derivation]] | Task rules + fingerprints |
| [[backend.app.services.task_migration]] | Safe derivation upgrades |

## Critical classes

- [[backend.app.db.repositories.Repository]]
- [[backend.app.mail.providers.gmail.GmailProvider]]
- [[backend.app.mail.eligibility.MailEligibilityPolicy]]
- [[backend.app.ai.ollama_client.OllamaClient]]
- [[backend.app.ai.service.AIService]]
- [[backend.app.services.task_migration.TaskMigrationService]]

## Related

- [[Backend Architecture]]
- [[Backend Code Map]]
- [[API Overview]]

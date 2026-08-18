---
type: architecture
layer: backend
status: active
tags:
  - backend
  - architecture
---

# Backend Code Map

Human-readable map of the backend source tree (`backend/`).

```mermaid
flowchart TD
    M[app.main] --> C[app.config]
    M --> R[db.repositories]
    R --> D[db.database]
    M --> G[mall.providers.gmail]
    G --> E[mail.eligibility]
    G --> B[mail.backfill]
    G --> F[mail.fingerprint]
    M --> A[ai.service]
    A --> O[ai.ollama_client]
    M --> T[services.task_derivation]
    M --> TM[services.task_migration]
    T --> S[schemas]
    A --> S
    G --> S
    R --> S
    M --> SC[db.secure_store]
```

## File-by-file

| Path | What lives there |
|---|---|
| `app/main.py` | All routes, SSE hub, `_analysis_worker`, `_backfill_worker`, lifespan, OAuth helpers, `_derive_and_save_tasks`, `_briefing_eligible_emails` |
| `app/config.py` | `Settings` (env → pydantic) |
| `app/schemas.py` | All Pydantic contracts incl. AI schemas |
| `db/database.py` | `SCHEMA`, `INDEXES`, `FTS_SCHEMA`, `connect`, `_migrate`, `transaction` |
| `db/repositories.py` | `Repository`: every SQL statement |
| `db/secure_store.py` | DPAPI `encrypt_token`/`decrypt_token` |
| `mail/eligibility.py` | Labels, states, categories, `MailEligibilityPolicy` |
| `mail/backfill.py` | Typed backfill cursor model |
| `mail/fingerprint.py` / `briefing_fingerprint.py` | Cache keys |
| `mail/normalizer.py` | Legacy CSV normalization |
| `mail/providers/gmail.py` | `GmailProvider` |
| `ai/ollama_client.py` | `OllamaClient` + error classes + `InferenceMetrics` |
| `ai/service.py` | `AIService`: prompts, sanitization, count overrides |
| `services/task_derivation.py` | Derivation gates, fingerprints, rebuild |
| `services/task_migration.py` | `TaskMigrationService` reconciliation |

## Related

- [[Backend Overview]]
- [[Entry Points]]
- [[Dependency Map]]

---
type: architecture
layer: backend
status: active
tags:
  - backend
  - architecture
---

# API Overview

FastAPI on `127.0.0.1:8765` ([[Local API Security]]). All routes live in [[backend.app.main]]; one generated note per endpoint in `99 - Generated/API Endpoints`.

## Groups

| Group | Endpoints |
|---|---|
| Health/config | [[GET --health]], [[GET --api-config]] |
| Accounts | [[GET --api-accounts]], [[POST --api-accounts-gmail-connect]], [[GET --api-accounts-gmail-callback]], [[DELETE --api-accounts-{account_id}]] |
| Sync | [[POST --api-accounts-{account_id}-sync]] |
| Backfill | [[POST --api-accounts-{account_id}-backfill]], [[POST --api-accounts-{account_id}-backfill-pause]], [[GET --api-accounts-{account_id}-backfill]] |
| Emails | [[GET --api-emails]], [[GET --api-emails-{email_id}]], [[GET --api-emails-counts]], [[POST --api-emails-import]], [[POST --api-emails-{email_id}-analyze]], [[POST --api-emails-analyze]], [[POST --api-emails-{email_id}-draft]] |
| Briefing | [[GET --api-briefing]], [[POST --api-briefing-generate]] |
| Tasks | [[GET --api-tasks]], [[POST --api-tasks-{task_id}-toggle]], [[DELETE --api-tasks-{task_id}]] |
| Progress | [[GET --api-analysis-progress]] (SSE), [[GET --api-analysis-status]] |

## Conventions

- Errors: FastAPI `detail` strings, or `{error:{code,message,details}}` JSON for OAuth/AI errors; typed AI failures map to 502/503/504 handlers.
- Eligibility is server-enforced: scope (`inbox|all`), category tabs (inbox only), `kind` (All Mail refinement), and the analyze-409 for excluded mail.
- Pagination: `limit`/`offset` on list endpoints; virtualization relies on it ([[ADR-012 - Inbox Virtualization]]).

## Related

- [[API Map]]
- [[Backend Overview]]

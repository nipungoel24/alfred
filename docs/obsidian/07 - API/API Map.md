---
type: architecture
layer: backend
status: active
tags:
  - backend
  - architecture
---

# API Map

Frontend feature → endpoint → handler → service → repository/table. Built from the actual implementation.

| UI | Endpoint | Handler | Service path | Data |
|---|---|---|---|---|
| Header status | [[GET --health]] | `health` | [[backend.app.ai.service.AIService.health|AIService.health]] | — |
| AccountsPage | [[GET --api-accounts]] | `get_accounts` | — | [[accounts]] + backfill status |
| AccountsPage | [[POST --api-accounts-gmail-connect]] | `connect_gmail` | [[backend.app.mail.providers.gmail.GmailProvider.get_auth_url|get_auth_url]] | — |
| OAuth popup | [[GET --api-accounts-gmail-callback]] | `gmail_callback` | `exchange_code` → [[backend.app.db.secure_store|secure_store]] | [[accounts]], [[credentials]] |
| AccountsPage Sync | [[POST --api-accounts-{account_id}-sync]] | `sync_account` | [[backend.app.mail.providers.gmail.GmailProvider.sync_messages|sync_messages]] → enqueue | [[emails]], [[jobs]] |
| MailWorkspace status | [[GET --api-accounts-{account_id}-backfill]] | `backfill_status` | [[backend.app.mail.backfill]] | [[accounts]] |
| MailWorkspace resume/pause | [[POST --api-accounts-{account_id}-backfill]] / [[POST --api-accounts-{account_id}-backfill-pause]] | `backfill_account` / `pause_backfill` | arms durable job | [[jobs]] |
| Mail list (all views) | [[GET --api-emails]] | `get_emails` | `Repository.emails_filtered` + cached analyses | [[emails]], [[email_analysis]] |
| Counts | [[GET --api-emails-counts]] | `get_email_counts` | `Repository.email_counts` | [[emails]] |
| Reader | [[GET --api-emails-{email_id}]] | `get_email` | `Repository.email` | [[emails]], [[email_analysis]] |
| Intelligence | [[POST --api-emails-{email_id}-analyze]] | `analyze` | [[backend.app.ai.service.AIService.analyze_email|analyze_email]] → derive | [[email_analysis]], [[tasks]] |
| Analyze all | [[POST --api-emails-analyze]] | `analyze_all` | policy enqueue | [[jobs]] |
| Draft | [[POST --api-emails-{email_id}-draft]] | `draft` | [[backend.app.ai.service.AIService.draft_reply|draft_reply]] | [[emails]] (thread) |
| Overview | [[GET --api-briefing]] / [[POST --api-briefing-generate]] | `briefing_get`/`generate_briefing` | `_briefing_eligible_emails` → [[backend.app.ai.service.AIService.generate_inbox_briefing|generate_inbox_briefing]] | [[emails]], [[email_analysis]], [[inbox_briefing]] |
| Tasks | [[GET --api-tasks]] / [[POST --api-tasks-{task_id}-toggle]] / [[DELETE --api-tasks-{task_id}]] | `get_tasks` etc. | `Repository.active_tasks` | [[tasks]] |
| Progress pill | [[GET --api-analysis-progress]] | `analysis_progress` | SSE hub | — |

## Related

- [[API Overview]]
- [[Frontend Data Fetch Flow]]

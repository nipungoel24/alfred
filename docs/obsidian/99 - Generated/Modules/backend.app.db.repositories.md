---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.app.db.repositories
source: backend/app/db/repositories.py
status: active
tags: [module, backend]
---

# backend.app.db.repositories

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/app/db/repositories.py`

## Imports

- `Email` ← `backend.app.schemas.Email`
- `EmailAccount` ← `backend.app.schemas.EmailAccount`
- `EmailAnalysis` ← `backend.app.schemas.EmailAnalysis`
- `InboxBriefing` ← `backend.app.schemas.InboxBriefing`
- `MailEligibilityPolicy` ← `backend.app.mail.eligibility.MailEligibilityPolicy`
- `Task` ← `backend.app.schemas.Task`
- `connect` ← `backend.app.db.database.connect`
- `datetime` ← `datetime.datetime`
- `gmail_category_from_labels` ← `backend.app.mail.eligibility.gmail_category_from_labels`
- `json` ← `json`
- `mailbox_state_from_labels` ← `backend.app.mail.eligibility.mailbox_state_from_labels`
- `timezone` ← `datetime.timezone`
- `transaction` ← `backend.app.db.database.transaction`

## Classes

- [[backend.app.db.repositories.Repository|Repository]]

## Functions

- [[backend.app.db.repositories.Repository.__init__|__init__]]
- [[backend.app.db.repositories.Repository._task_from_row|_task_from_row]]
- [[backend.app.db.repositories.Repository._update_fts_one|_update_fts_one]]
- [[backend.app.db.repositories.Repository.account|account]]
- [[backend.app.db.repositories.Repository.accounts|accounts]]
- [[backend.app.db.repositories.Repository.active_tasks|active_tasks]]
- [[backend.app.db.repositories.Repository.all_analyses_with_emails|all_analyses_with_emails]]
- [[backend.app.db.repositories.Repository.cached_analysis|cached_analysis]]
- [[backend.app.db.repositories.Repository.cached_briefing|cached_briefing]]
- [[backend.app.db.repositories.Repository.close|close]]
- [[backend.app.db.repositories.Repository.completed_job_count|completed_job_count]]
- [[backend.app.db.repositories.Repository.credentials|credentials]]
- [[backend.app.db.repositories.Repository.delete_account|delete_account]]
- [[backend.app.db.repositories.Repository.delete_email|delete_email]]
- [[backend.app.db.repositories.Repository.delete_task|delete_task]]
- [[backend.app.db.repositories.Repository.delete_tasks_by_derivation_version|delete_tasks_by_derivation_version]]
- [[backend.app.db.repositories.Repository.eligible_emails_without_analysis|eligible_emails_without_analysis]]
- [[backend.app.db.repositories.Repository.email|email]]
- [[backend.app.db.repositories.Repository.email_count|email_count]]
- [[backend.app.db.repositories.Repository.email_counts|email_counts]]
- [[backend.app.db.repositories.Repository.email_eligibility|email_eligibility]]
- [[backend.app.db.repositories.Repository.email_exists|email_exists]]
- [[backend.app.db.repositories.Repository.emails|emails]]
- [[backend.app.db.repositories.Repository.emails_by_thread|emails_by_thread]]
- [[backend.app.db.repositories.Repository.emails_filtered|emails_filtered]]
- [[backend.app.db.repositories.Repository.emails_missing_labels|emails_missing_labels]]
- [[backend.app.db.repositories.Repository.enqueue_job|enqueue_job]]
- [[backend.app.db.repositories.Repository.failed_job_count|failed_job_count]]
- [[backend.app.db.repositories.Repository.job|job]]
- [[backend.app.db.repositories.Repository.mark_email_excluded|mark_email_excluded]]
- [[backend.app.db.repositories.Repository.next_job|next_job]]
- [[backend.app.db.repositories.Repository.pending_job_count|pending_job_count]]
- [[backend.app.db.repositories.Repository.promote_due_jobs|promote_due_jobs]]
- [[backend.app.db.repositories.Repository.rearm_terminal_job|rearm_terminal_job]]
- [[backend.app.db.repositories.Repository.record_inference_metric|record_inference_metric]]
- [[backend.app.db.repositories.Repository.requeue_job|requeue_job]]
- [[backend.app.db.repositories.Repository.reset_retryable_jobs|reset_retryable_jobs]]
- [[backend.app.db.repositories.Repository.retry_job_with_backoff|retry_job_with_backoff]]
- [[backend.app.db.repositories.Repository.save_account|save_account]]
- [[backend.app.db.repositories.Repository.save_analysis|save_analysis]]
- [[backend.app.db.repositories.Repository.save_briefing|save_briefing]]
- [[backend.app.db.repositories.Repository.save_credentials|save_credentials]]
- [[backend.app.db.repositories.Repository.save_task|save_task]]
- [[backend.app.db.repositories.Repository.save_tasks_batch|save_tasks_batch]]
- [[backend.app.db.repositories.Repository.search_emails|search_emails]]
- [[backend.app.db.repositories.Repository.task|task]]
- [[backend.app.db.repositories.Repository.task_exists_by_fingerprint|task_exists_by_fingerprint]]
- [[backend.app.db.repositories.Repository.tasks|tasks]]
- [[backend.app.db.repositories.Repository.tasks_by_email|tasks_by_email]]
- [[backend.app.db.repositories.Repository.tasks_by_thread|tasks_by_thread]]
- [[backend.app.db.repositories.Repository.update_email_labels|update_email_labels]]
- [[backend.app.db.repositories.Repository.update_job_status|update_job_status]]
- [[backend.app.db.repositories.Repository.upsert_email|upsert_email]]
- [[backend.app.db.repositories.Repository.upsert_email_commit|upsert_email_commit]]
- [[backend.app.db.repositories.Repository.upsert_emails_batch|upsert_emails_batch]]

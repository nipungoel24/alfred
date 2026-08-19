---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.app.main
source: backend/app/main.py
status: active
tags: [module, backend]
---

# backend.app.main

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/app/main.py`

## Imports

- `AIService` ← `backend.app.ai.service.AIService`
- `BRIEFING_SCHEMA_VERSION` ← `backend.app.mail.briefing_fingerprint.BRIEFING_SCHEMA_VERSION`
- `BackfillState` ← `backend.app.mail.eligibility.BackfillState`
- `CORSMiddleware` ← `fastapi.middleware.cors.CORSMiddleware`
- `DERIVATION_VERSION` ← `backend.app.services.task_derivation.DERIVATION_VERSION`
- `Email` ← `backend.app.schemas.Email`
- `EmailAccount` ← `backend.app.schemas.EmailAccount`
- `EmailAnalysis` ← `backend.app.schemas.EmailAnalysis`
- `FastAPI` ← `fastapi.FastAPI`
- `File` ← `fastapi.File`
- `GmailCategory` ← `backend.app.mail.eligibility.GmailCategory`
- `GmailProvider` ← `backend.app.mail.providers.gmail.GmailProvider`
- `HTMLResponse` ← `fastapi.responses.HTMLResponse`
- `HTTPException` ← `fastapi.HTTPException`
- `InboxBriefing` ← `backend.app.schemas.InboxBriefing`
- `JSONResponse` ← `fastapi.responses.JSONResponse`
- `MailEligibilityPolicy` ← `backend.app.mail.eligibility.MailEligibilityPolicy`
- `OllamaClient` ← `backend.app.ai.ollama_client.OllamaClient`
- `OllamaInvalidResponse` ← `backend.app.ai.ollama_client.OllamaInvalidResponse`
- `OllamaModelMissing` ← `backend.app.ai.ollama_client.OllamaModelMissing`
- `OllamaTimeout` ← `backend.app.ai.ollama_client.OllamaTimeout`
- `OllamaUnavailable` ← `backend.app.ai.ollama_client.OllamaUnavailable`
- `Query` ← `fastapi.Query`
- `Repository` ← `backend.app.db.repositories.Repository`
- `Request` ← `fastapi.Request`
- `StreamingResponse` ← `fastapi.responses.StreamingResponse`
- `Task` ← `backend.app.schemas.Task`
- `UploadFile` ← `fastapi.UploadFile`
- `asynccontextmanager` ← `contextlib.asynccontextmanager`
- `asyncio` ← `asyncio`
- `base64` ← `base64`
- `briefing_fingerprint` ← `backend.app.mail.briefing_fingerprint.briefing_fingerprint`
- `content_fingerprint` ← `backend.app.mail.fingerprint.content_fingerprint`
- `csv` ← `csv`
- `datetime` ← `datetime.datetime`
- `decrypt_token` ← `backend.app.db.secure_store.decrypt_token`
- `derive_tasks` ← `backend.app.services.task_derivation.derive_tasks`
- `dump_cursor` ← `backend.app.mail.backfill.dump_cursor`
- `encrypt_token` ← `backend.app.db.secure_store.encrypt_token`
- `get_settings` ← `backend.app.config.get_settings`
- `hashlib` ← `hashlib`
- `httpx` ← `httpx`
- `io` ← `io`
- `json` ← `json`
- `logging` ← `logging`
- `normalize_cursor` ← `backend.app.mail.backfill.normalize_cursor`
- `normalized_email` ← `backend.app.mail.normalizer.normalized_email`
- `rebuild_tasks_from_analyses` ← `backend.app.services.task_derivation.rebuild_tasks_from_analyses`
- `record_failure` ← `backend.app.mail.backfill.record_failure`
- `secrets` ← `secrets`
- `set_state` ← `backend.app.mail.backfill.set_state`
- `status_payload` ← `backend.app.mail.backfill.status_payload`
- `timedelta` ← `datetime.timedelta`
- `timezone` ← `datetime.timezone`
- `uuid` ← `uuid`

## Functions

- [[backend.app.main._analysis_worker|_analysis_worker]]
- [[backend.app.main._backfill_estimate_once|_backfill_estimate_once]]
- [[backend.app.main._backfill_job_id|_backfill_job_id]]
- [[backend.app.main._backfill_worker|_backfill_worker]]
- [[backend.app.main._briefing_eligible_emails|_briefing_eligible_emails]]
- [[backend.app.main._broadcast_progress|_broadcast_progress]]
- [[backend.app.main._derive_and_save_tasks|_derive_and_save_tasks]]
- [[backend.app.main._ensure_backfill_job|_ensure_backfill_job]]
- [[backend.app.main._label_backfill|_label_backfill]]
- [[backend.app.main._mark_backfill_failure|_mark_backfill_failure]]
- [[backend.app.main._oauth_callback_page|_oauth_callback_page]]
- [[backend.app.main._set_backfill_state|_set_backfill_state]]
- [[backend.app.main.analysis_progress|analysis_progress]]
- [[backend.app.main.analysis_progress.event_stream|event_stream]]
- [[backend.app.main.analysis_status|analysis_status]]
- [[backend.app.main.analyze|analyze]]
- [[backend.app.main.analyze_all|analyze_all]]
- [[backend.app.main.backfill_account|backfill_account]]
- [[backend.app.main.backfill_status|backfill_status]]
- [[backend.app.main.briefing_get|briefing_get]]
- [[backend.app.main.config|config]]
- [[backend.app.main.connect_gmail|connect_gmail]]
- [[backend.app.main.delete_account|delete_account]]
- [[backend.app.main.delete_task|delete_task]]
- [[backend.app.main.draft|draft]]
- [[backend.app.main.generate_briefing|generate_briefing]]
- [[backend.app.main.generate_pkce_pair|generate_pkce_pair]]
- [[backend.app.main.get_accounts|get_accounts]]
- [[backend.app.main.get_email|get_email]]
- [[backend.app.main.get_email_counts|get_email_counts]]
- [[backend.app.main.get_emails|get_emails]]
- [[backend.app.main.get_tasks|get_tasks]]
- [[backend.app.main.gmail_callback|gmail_callback]]
- [[backend.app.main.health|health]]
- [[backend.app.main.import_csv|import_csv]]
- [[backend.app.main.lifespan|lifespan]]
- [[backend.app.main.ollama_invalid_handler|ollama_invalid_handler]]
- [[backend.app.main.ollama_model_missing_handler|ollama_model_missing_handler]]
- [[backend.app.main.ollama_timeout_handler|ollama_timeout_handler]]
- [[backend.app.main.ollama_unavailable_handler|ollama_unavailable_handler]]
- [[backend.app.main.pause_backfill|pause_backfill]]
- [[backend.app.main.runtime_token_middleware|runtime_token_middleware]]
- [[backend.app.main.shutdown_backend|shutdown_backend]]
- [[backend.app.main.sync_account|sync_account]]
- [[backend.app.main.toggle_task|toggle_task]]

## Constants

- `BACKFILL_JOB_TYPE`
- `BACKFILL_PAGE_INTERVAL_S`
- `BACKFILL_PAGE_SIZE`
- `BACKFILL_PRIORITY`
- `OAUTH_STATES`
- `VALID_CATEGORIES`
- `WORKER_CONCURRENCY`

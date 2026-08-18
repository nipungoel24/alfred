---
type: architecture
layer: test
status: active
tags:
  - test
---

# Test Coverage Map

Critical paths → the tests that pin them. (No numeric coverage claim — coverage tooling has not been run.)

| Path | Tests |
|---|---|
| OAuth connect/callback | [[backend.tests.test_gmail_mock.test_gmail_oauth_url_generation]], token exchange test |
| Initial sync | [[backend.tests.test_gmail_mock.test_gmail_sync_initial]] |
| Incremental + deletions | [[backend.tests.test_gmail_mock.test_gmail_sync_incremental]] |
| History expiry recovery | [[backend.tests.test_gmail_mock.test_gmail_sync_history_expired_recovery]] |
| Load-older pagination | [[backend.tests.test_gmail_mock.test_gmail_sync_load_older]] |
| HTML sanitization | [[backend.tests.test_gmail_mock.test_gmail_html_sanitisation]], [[backend.tests.test_extended.test_malicious_html_normalization]] |
| Mailbox policy corpus | [[backend.tests.test_eligibility]] (all transition tests) |
| Label history mutation | [[backend.tests.test_eligibility.test_history_label_changes_refresh_via_metadata]] |
| Spam arrival never cached | [[backend.tests.test_eligibility.test_history_spam_arrival_is_never_cached]] |
| All Mail scopes/kind | [[backend.tests.test_allmail]] |
| Backfill durability | [[backend.tests.test_backfill_jobs]] |
| Analysis queue (worker guard) | [[backend.tests.test_eligibility.test_email_api_excluded_mail_never_listed]] |
| Task derivation gates | [[backend.tests.test_task_derivation]] |
| Task migration safety | [[backend.tests.test_task_migration]] |
| API flows | [[backend.tests.test_extended.test_api_endpoint_flows]] |
| Ollama error taxonomy | [[backend.tests.test_ollama_mock]] |
| Frontend theme | [[frontend.src.theme.ThemeProvider.test]], [[frontend.src.theme.themeStore.test]] |
| Frontend workspace | [[frontend.src.mail.MailWorkspace.test]] |
| Frontend shell/header | `frontend/tests/app.test.tsx`, [[frontend.src.layout.WorkspaceHeader.test]] |
| Docs generator | `tools/docs/tests/test_generator.py` |

## Gaps worth knowing

- Real-mailbox acceptance is manual ([[Gmail E2E Testing]]) — deliberate: the mailbox must never be reset.
- Worker-level concurrency/races are covered by design (single worker + durable jobs), not stress tests.

## Related

- [[Testing Strategy]]
- [[Critical Execution Paths]]

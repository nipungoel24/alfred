---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.fingerprint
qualified_name: backend.app.mail.fingerprint.content_fingerprint
source: backend/app/mail/fingerprint.py
line: 4
status: active
tags: [gmail, function]
---

# content_fingerprint

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `content_fingerprint` in `backend/app/mail/fingerprint.py`.

## Location

`backend/app/mail/fingerprint.py:4`

## Signature

```python
(email: Email) -> str
```

## Parameters

- `email` (`Email`)

## Returns

`str`

## Calls

- [[backend.app.mail.normalizer.normalize_text|normalize_text]] (calls)
- `sha256` (`hashlib.sha256`, calls-inferred)

## Called By

- [[backend.app.mail.providers.gmail.GmailProvider.backfill_messages|backfill_messages]]
- [[backend.app.mail.providers.gmail.GmailProvider.sync_messages|sync_messages]]
- [[backend.app.main._analysis_worker|_analysis_worker]]
- [[backend.app.main._briefing_eligible_emails|_briefing_eligible_emails]]
- [[backend.app.main.analyze|analyze]]
- [[backend.app.main.analyze_all|analyze_all]]
- [[backend.app.main.get_email|get_email]]
- [[backend.app.main.get_emails|get_emails]]
- [[backend.app.main.import_csv|import_csv]]
- [[backend.app.main.sync_account|sync_account]]
- [[backend.tests.test_core.test_analysis_cache_invalidates_content_and_model|test_analysis_cache_invalidates_content_and_model]]
- [[backend.tests.test_core.test_briefing_cache_invalidates_when_analysis_changes|test_briefing_cache_invalidates_when_analysis_changes]]
- [[backend.tests.test_core.test_fingerprint_is_deterministic_and_changes|test_fingerprint_is_deterministic_and_changes]]
- [[backend.tests.test_extended.test_cache_hit_and_invalidation|test_cache_hit_and_invalidation]]
- [[backend.tests.test_extended.test_persistence_restart|test_persistence_restart]]

## Side Effects

- none statically observed

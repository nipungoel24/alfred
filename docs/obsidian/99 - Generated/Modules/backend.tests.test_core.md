---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.tests.test_core
source: backend/tests/test_core.py
status: active
tags: [module, backend]
---

# backend.tests.test_core

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/tests/test_core.py`

## Imports

- `Category` ← `backend.app.schemas.Category`
- `Email` ← `backend.app.schemas.Email`
- `EmailAnalysis` ← `backend.app.schemas.EmailAnalysis`
- `InboxBriefing` ← `backend.app.schemas.InboxBriefing`
- `Path` ← `pathlib.Path`
- `Priority` ← `backend.app.schemas.Priority`
- `Repository` ← `backend.app.db.repositories.Repository`
- `briefing_fingerprint` ← `backend.app.mail.briefing_fingerprint.briefing_fingerprint`
- `content_fingerprint` ← `backend.app.mail.fingerprint.content_fingerprint`
- `normalized_email` ← `backend.app.mail.normalizer.normalized_email`

## Functions

- [[backend.tests.test_core.analysis|analysis]]
- [[backend.tests.test_core.email|email]]

## Tests

- [[backend.tests.test_core.test_analysis_cache_invalidates_content_and_model|test_analysis_cache_invalidates_content_and_model]]
- [[backend.tests.test_core.test_briefing_cache_invalidates_when_analysis_changes|test_briefing_cache_invalidates_when_analysis_changes]]
- [[backend.tests.test_core.test_fingerprint_is_deterministic_and_changes|test_fingerprint_is_deterministic_and_changes]]
- [[backend.tests.test_core.test_normalizer_treats_html_as_safe_text|test_normalizer_treats_html_as_safe_text]]

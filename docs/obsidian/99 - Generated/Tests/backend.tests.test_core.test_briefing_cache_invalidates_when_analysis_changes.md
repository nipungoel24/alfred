---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_core
qualified_name: backend.tests.test_core.test_briefing_cache_invalidates_when_analysis_changes
source: backend/tests/test_core.py
line: 27
status: active
tags: [test, function, test]
---

# test_briefing_cache_invalidates_when_analysis_changes

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_briefing_cache_invalidates_when_analysis_changes` in `backend/tests/test_core.py`.

## Location

`backend/tests/test_core.py:27`

## Signature

```python
(tmp_path: Path)
```

## Parameters

- `tmp_path` (`Path`)

## Calls

- [[backend.app.db.repositories.Repository|Repository]] (calls)
- [[backend.app.mail.briefing_fingerprint.briefing_fingerprint|briefing_fingerprint]] (calls)
- [[backend.app.mail.fingerprint.content_fingerprint|content_fingerprint]] (calls)
- [[backend.app.schemas.InboxBriefing|InboxBriefing]] (calls)

## Side Effects

- none statically observed

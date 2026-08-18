---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.briefing_fingerprint
qualified_name: backend.app.mail.briefing_fingerprint.briefing_fingerprint
source: backend/app/mail/briefing_fingerprint.py
line: 7
status: active
tags: [gmail, function]
---

# briefing_fingerprint

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Fingerprint compact analyses, never raw email bodies.

## Location

`backend/app/mail/briefing_fingerprint.py:7`

## Signature

```python
(emails: list[Email], model: str) -> str
```

## Parameters

- `emails` (`list[Email]`)
- `model` (`str`)

## Returns

`str`

## Calls

- `sha256` (`hashlib.sha256`, calls-inferred)
- `dumps` (`json.dumps`, calls-inferred)

## Called By

- [[backend.app.main.generate_briefing|generate_briefing]]
- [[backend.tests.test_core.test_briefing_cache_invalidates_when_analysis_changes|test_briefing_cache_invalidates_when_analysis_changes]]

## Side Effects

- none statically observed

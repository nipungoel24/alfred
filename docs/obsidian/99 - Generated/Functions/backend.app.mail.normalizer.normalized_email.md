---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.normalizer
qualified_name: backend.app.mail.normalizer.normalized_email
source: backend/app/mail/normalizer.py
line: 12
status: active
tags: [gmail, function]
---

# normalized_email

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `normalized_email` in `backend/app/mail/normalizer.py`.

## Location

`backend/app/mail/normalizer.py:12`

## Signature

```python
(row: dict, index: int) -> Email
```

## Parameters

- `row` (`dict`)
- `index` (`int`)

## Returns

`Email`

## Calls

- [[backend.app.schemas.Email|Email]] (calls)
- `fromisoformat` (`datetime.datetime.fromisoformat`, calls-inferred)

## Called By

- [[backend.app.main.import_csv|import_csv]]
- [[backend.tests.test_core.test_normalizer_treats_html_as_safe_text|test_normalizer_treats_html_as_safe_text]]
- [[backend.tests.test_extended.test_malicious_html_normalization|test_malicious_html_normalization]]

## Side Effects

- none statically observed

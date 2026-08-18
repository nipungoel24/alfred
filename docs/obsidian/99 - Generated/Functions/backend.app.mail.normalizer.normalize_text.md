---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.normalizer
qualified_name: backend.app.mail.normalizer.normalize_text
source: backend/app/mail/normalizer.py
line: 6
status: active
tags: [gmail, function]
---

# normalize_text

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `normalize_text` in `backend/app/mail/normalizer.py`.

## Location

`backend/app/mail/normalizer.py:6`

## Signature

```python
(value: object) -> str
```

## Parameters

- `value` (`object`)

## Returns

`str`

## Calls

- `unescape` (`html.unescape`, calls-inferred)
- `sub` (`re.sub`, calls-inferred)

## Called By

- [[backend.app.mail.fingerprint.content_fingerprint|content_fingerprint]]

## Side Effects

- none statically observed

---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main.import_csv
source: backend/app/main.py
line: 865
status: active
tags: [backend, function, endpoint]
---

# import_csv

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `import_csv` in `backend/app/main.py`.

## Route

`POST /api/emails/import`

## Location

`backend/app/main.py:865`

## Signature

```python
(file: UploadFile = File(...))
```

## Parameters

- `file` (`UploadFile`)

## Calls

- [[backend.app.mail.fingerprint.content_fingerprint|content_fingerprint]] (calls)
- [[backend.app.mail.normalizer.normalized_email|normalized_email]] (calls)
- `DictReader` (`csv.DictReader`, calls-inferred)
- `StringIO` (`io.StringIO`, calls-inferred)

## Side Effects

- async I/O

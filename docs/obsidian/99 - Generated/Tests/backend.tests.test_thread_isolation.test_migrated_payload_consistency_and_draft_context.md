---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_thread_isolation
qualified_name: backend.tests.test_thread_isolation.test_migrated_payload_consistency_and_draft_context
source: backend/tests/test_thread_isolation.py
line: 282
status: active
tags: [test, function, test]
---

# test_migrated_payload_consistency_and_draft_context

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Legacy DB -> migrate -> payload/columns agree -> REAL draft endpoint

## Location

`backend/tests/test_thread_isolation.py:282`

## Signature

```python
(tmp_path, monkeypatch, provider)
```

## Parameters

- `tmp_path`
- `monkeypatch`
- `provider`

## Calls

- [[backend.app.mail.identity.scoped_email_id|scoped_email_id]] (calls)
- [[backend.app.mail.identity.scoped_thread_id|scoped_thread_id]] (calls)
- [[backend.app.schemas.Email|Email]] (calls)
- `TestClient` (`fastapi.testclient.TestClient`, calls-inferred)

## Writes

- [[table_emails]]

## Side Effects

- SQLite; network (HTTP)

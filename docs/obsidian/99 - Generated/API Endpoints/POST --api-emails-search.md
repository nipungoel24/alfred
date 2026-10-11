---
type: endpoint
generated: true
layer: backend
qualified_name: backend.app.main.search_emails_structured
source: backend/app/main.py
line: 1133
status: active
tags: [backend, function, endpoint, endpoint]
---

# POST /api/emails/search

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Structured search with filters applied at the database level.

## Handler

[[backend.app.main.search_emails_structured|search_emails_structured]]

## Location

`backend/app/main.py:1133`

## Parameters

- `filters` (`SearchFilters`)
- `account_id` (`str | None`)
- `limit` (`int`)
- `offset` (`int`)

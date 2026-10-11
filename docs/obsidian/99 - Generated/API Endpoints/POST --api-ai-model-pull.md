---
type: endpoint
generated: true
layer: backend
qualified_name: backend.app.main.ai_model_pull
source: backend/app/main.py
line: 1058
status: active
tags: [backend, function, endpoint, endpoint]
---

# POST /api/ai/model/pull

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Start downloading a model. Idempotent — returns live progress.

## Handler

[[backend.app.main.ai_model_pull|ai_model_pull]]

## Location

`backend/app/main.py:1058`

## Parameters

- `body` (`ModelPullRequest | None`)

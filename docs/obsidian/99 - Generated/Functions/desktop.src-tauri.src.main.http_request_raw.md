---
type: function
generated: true
language: rust
layer: backend
module: desktop.src-tauri.src.main
qualified_name: desktop.src-tauri.src.main.http_request_raw
source: desktop/src-tauri/src/main.rs
line: 1045
status: active
tags: [backend, function]
---

# http_request_raw

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `http_request_raw` in `desktop/src-tauri/src/main.rs`.

## Location

`desktop/src-tauri/src/main.rs:1045`

## Signature

```rust
fn http_request_raw(
    port: u16,
    method: &str,
    path: &str,
    token: &str,
) -> Result<RawResponse, String>
```

## Parameters

- `port` (`u16`)
- `method` (`&str`)
- `path` (`&str`)
- `token` (`&str`)

## Returns

`Result<RawResponse, String>`

## Side Effects

- none statically observed

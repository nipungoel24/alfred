---
type: function
generated: true
language: rust
layer: backend
module: desktop.src-tauri.src.main
qualified_name: desktop.src-tauri.src.main.backend_info
source: desktop/src-tauri/src/main.rs
line: 446
status: active
tags: [backend, function]
---

# backend_info

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `backend_info` in `desktop/src-tauri/src/main.rs`.

## Location

`desktop/src-tauri/src/main.rs:446`

## Signature

```rust
fn backend_info(
    supervisor: State<'_, Arc<tokio::sync::Mutex<BackendSupervisor>>>,
) -> Result<BackendInfo, String>
```

## Parameters

- `supervisor` (`State<'_`)
- `Arc<tokio` (`Mutex<BackendSupervisor>>>`)

## Returns

`Result<BackendInfo, String>`

## Side Effects

- none statically observed

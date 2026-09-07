---
type: function
generated: true
language: rust
layer: backend
module: desktop.src-tauri.src.main
qualified_name: desktop.src-tauri.src.main.await_backend_ready
source: desktop/src-tauri/src/main.rs
line: 368
status: active
tags: [backend, function]
---

# await_backend_ready

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `await_backend_ready` in `desktop/src-tauri/src/main.rs`.

## Location

`desktop/src-tauri/src/main.rs:368`

## Signature

```rust
fn await_backend_ready(
    supervisor: tauri::State<'_, Arc<tokio::sync::Mutex<BackendSupervisor>>>,
) -> Result<BackendInfo, String>
```

## Parameters

- `supervisor` (`State<'_`)
- `Arc<tokio` (`Mutex<BackendSupervisor>>>`)

## Returns

`Result<BackendInfo, String>`

## Side Effects

- none statically observed

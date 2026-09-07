---
type: function
generated: true
language: rust
layer: backend
module: desktop.src-tauri.src.main
qualified_name: desktop.src-tauri.src.main.restart_backend
source: desktop/src-tauri/src/main.rs
line: 416
status: active
tags: [backend, function]
---

# restart_backend

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `restart_backend` in `desktop/src-tauri/src/main.rs`.

## Location

`desktop/src-tauri/src/main.rs:416`

## Signature

```rust
fn restart_backend(
    supervisor: tauri::State<'_, Arc<tokio::sync::Mutex<BackendSupervisor>>>,
) -> Result<(), String>
```

## Parameters

- `supervisor` (`State<'_`)
- `Arc<tokio` (`Mutex<BackendSupervisor>>>`)

## Returns

`Result<(), String>`

## Side Effects

- none statically observed

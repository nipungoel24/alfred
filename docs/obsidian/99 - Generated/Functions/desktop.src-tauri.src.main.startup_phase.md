---
type: function
generated: true
language: rust
layer: backend
module: desktop.src-tauri.src.main
qualified_name: desktop.src-tauri.src.main.startup_phase
source: desktop/src-tauri/src/main.rs
line: 1226
status: active
tags: [backend, function]
---

# startup_phase

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `startup_phase` in `desktop/src-tauri/src/main.rs`.

## Location

`desktop/src-tauri/src/main.rs:1226`

## Signature

```rust
fn startup_phase(
    supervisor: State<'_, Arc<tokio::sync::Mutex<BackendSupervisor>>>,
) -> Result<StartupStatus, String>
```

## Parameters

- `supervisor` (`State<'_`)
- `Arc<tokio` (`Mutex<BackendSupervisor>>>`)

## Returns

`Result<StartupStatus, String>`

## Side Effects

- none statically observed

---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.resources
qualified_name: backend.app.ai.resources.installed_ram_bytes
source: backend/app/ai/resources.py
line: 87
status: active
tags: [ai, function]
---

# installed_ram_bytes

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Physically installed RAM in bytes, or None when it cannot be read.

## Location

`backend/app/ai/resources.py:87`

## Signature

```python
() -> int | None
```

## Returns

`int | None`

## Calls

- `byref` (`ctypes.byref`, calls-inferred)
- `c_ulonglong` (`ctypes.c_ulonglong`, calls-inferred)
- `GetPhysicallyInstalledSystemMemory` (`ctypes.windll.kernel32.GetPhysicallyInstalledSystemMemory`, calls-inferred)
- `sysconf` (`os.sysconf`, calls-inferred)

## Called By

- [[backend.tests.test_model_pull.test_installed_ram_is_reported_as_a_real_value|test_installed_ram_is_reported_as_a_real_value]]
- [[backend.tests.test_model_pull.test_the_preflight_runs_against_this_machine|test_the_preflight_runs_against_this_machine]]

## Side Effects

- none statically observed

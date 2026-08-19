---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.app.config
source: backend/app/config.py
status: active
tags: [module, backend]
---

# backend.app.config

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/app/config.py`

## Imports

- `BaseModel` ← `pydantic.BaseModel`
- `Field` ← `pydantic.Field`
- `Path` ← `pathlib.Path`
- `lru_cache` ← `functools.lru_cache`
- `os` ← `os`
- `sys` ← `sys`

## Classes

- [[backend.app.config.Settings|Settings]]

## Functions

- [[backend.app.config._default_database_path|_default_database_path]]
- [[backend.app.config._load_dotenv_file|_load_dotenv_file]]
- [[backend.app.config._load_environment|_load_environment]]
- [[backend.app.config.get_settings|get_settings]]

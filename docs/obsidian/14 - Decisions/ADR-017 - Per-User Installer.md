---
type: adr
layer: meta
status: active
tags:
  - architecture
  - desktop
---

# ADR-017 - Per-User Installer (currentUser)

## Status

Accepted

## Context

Alfred is a single-user, local-first assistant. A per-machine install requires UAC elevation for every install/update and writes to Program Files; it provides no benefit for a product whose data lives in the user's AppData.

## Decision

NSIS bundle uses `installMode: currentUser`: installs to `%LOCALAPPDATA%\Alfred`, Start Menu shortcut + uninstall registration under the user hive, no elevation prompt.

## Consequences

- User data moved out of the install directory for new installs (`%LOCALAPPDATA%\AlfredData\alfred.sqlite3`; legacy installs keep the previous location — the data file is never migrated in place).
- Verified: uninstall removes binaries but **preserves** the SQLite database ([[Windows Packaging]]).

## Related Code

- `desktop/src-tauri/tauri.conf.json`
- `_default_database_path` in [[backend.app.config]]

## Related Documentation

- [[Windows Packaging]]
- [[Data Privacy]]

---
type: operations
layer: meta
status: active
tags:
  - backend
---

# Release Checklist

Ordered pre-release gate (desktop packaging status: see [[Project Status]]).

1. **Tests** — `py -3 -m pytest backend/tests -q`; frontend `npm test -- --run`, `npm run lint`, `npm run build`; docs `--check` + validator.
2. **Real-mailbox smoke** — incremental sync, one backfill page, category counts sane, spam/trash absent ([[Gmail E2E Testing]]).
3. **No secrets** — `.env` values absent from logs/docs; `validate_vault.py` clean ([[Data Privacy]]).
4. **Sidecar** — rebuild binary after any backend change ([[Building Backend Sidecar]]).
5. **Package** — NSIS bundle per [[Windows Packaging]]; smoke test install/launch/quit (sidecar killed on exit).
6. **Theme QA** — both themes across Mail/All Mail/Reader/Intelligence/Overview/Tasks/Deadlines/Accounts/Settings at 1280/1440/1920.

## Related

- [[Running Alfred]]
- [[Development Setup]]
- [[Project Status]]

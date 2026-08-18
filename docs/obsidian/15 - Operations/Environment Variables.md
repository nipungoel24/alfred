---
type: operations
layer: meta
status: active
tags:
  - backend
  - security
---

# Environment Variables

Variable names, purpose, and security classification. **Values are never documented.**

| Name | Purpose | Required | Default | Classification |
|---|---|---|---|---|
| `OLLAMA_BASE_URL` | Ollama API origin | No | `http://127.0.0.1:11434` | config |
| `OLLAMA_MODEL` | Model id | No | `qwen3:4b` | config |
| `ALFRED_HOST` | Backend bind address | No | `127.0.0.1` | config (keep loopback!) |
| `ALFRED_PORT` | Backend port | No | `8765` | config |
| `ALFRED_DATABASE_PATH` | SQLite location override | No | `%LOCALAPPDATA%/Alfred/alfred.sqlite3` | config |
| `GMAIL_CLIENT_ID` | Google OAuth client id | Yes (for connect) | placeholder → connect disabled | public-ish (app identity) |
| `GMAIL_CLIENT_SECRET` | Google OAuth client secret | Yes (for connect) | placeholder | **secret** |

Loaded by [[backend.app.config.Settings]] from `backend/.env` (dotenv). See `docs/GMAIL_SETUP.md` (see [[Google OAuth]]) for the Google Cloud steps.

## Related

- [[Model Configuration]]
- [[Google OAuth]]

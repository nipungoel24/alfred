# Local API

The backend binds to `127.0.0.1:8765` by default.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Backend and local AI readiness |
| GET | `/api/config` | Safe runtime configuration |
| GET | `/api/emails` | List/filter persisted messages |
| GET | `/api/emails/{id}` | Message and cached analysis |
| POST | `/api/emails/import` | Import a CSV multipart file |
| POST | `/api/emails/analyze` | Analyze uncached messages |
| POST | `/api/emails/{id}/analyze` | Analyze one message |
| POST | `/api/emails/{id}/draft` | Lazily generate a draft |
| GET/POST | `/api/briefing`, `/api/briefing/generate` | Build briefing from compact persisted analyses |

Unavailable Ollama responses use HTTP 503 and `{ "error": { "code": "OLLAMA_UNAVAILABLE", "message": "...", "details": { "model": "..." }}}`.

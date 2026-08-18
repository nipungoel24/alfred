---
type: operations
layer: meta
status: active
tags:
  - backend
---

# Development Setup

Prerequisites and first-run steps for developing Alfred.

## Prerequisites

- Python 3.12+ (`py -3`), Node 22+, npm.
- Ollama installed with `qwen3:4b` pulled (`ollama pull qwen3:4b`).
- Gmail OAuth client credentials (see `docs/GMAIL_SETUP.md` (see [[Google OAuth]]) and [[Environment Variables]]).
- (Optional) Rust/Tauri toolchain for desktop packaging.

## Backend

```powershell
py -3 -m pip install -r requirements.txt
py -3 -m uvicorn app.main:app --host 127.0.0.1 --port 8765 --app-dir backend
```

## Frontend

```powershell
cd frontend
npm install
npm run dev        # http://localhost:5173
```

## Desktop (optional)

See [[Building Backend Sidecar]] and [[Running Alfred]].

## Tests

```powershell
py -3 -m pytest backend/tests -q
cd frontend; npm test -- --run; npm run lint; npm run build
```

## Documentation

```powershell
py tools/docs/generate_knowledge_graph.py            # regenerate symbol docs
py tools/docs/generate_knowledge_graph.py --check    # CI staleness gate
py tools/docs/validate_vault.py                      # links + secrets + canvases
```

## Related

- [[Environment Variables]]
- [[Running Alfred]]
- [[Debugging]]

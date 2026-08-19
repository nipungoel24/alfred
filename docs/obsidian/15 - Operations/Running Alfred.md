---
type: operations
layer: meta
status: active
tags:
  - backend
---

# Running Alfred

## Development mode (two terminals)

1. Backend: `py -3 -m uvicorn app.main:app --host 127.0.0.1 --port 8765 --app-dir backend` (no runtime token → API open on loopback, dev only).
2. Frontend: `cd frontend; npm run dev` → `http://localhost:5173`.

## Native development mode

```powershell
# Rust toolchain must be on PATH (or use full paths):
cargo tauri dev        # from desktop/src-tauri
```

This builds the Rust shell, starts Vite, spawns the sidecar (dynamic port + token), and opens the real native window.

## Installed release

Run the NSIS installer ([[Windows Packaging]]), then launch Alfred from the Start Menu. The app installs to `%LOCALAPPDATA%\Alfred`; user data lives at `%LOCALAPPDATA%\AlfredData\alfred.sqlite3` (legacy installs: `%LOCALAPPDATA%\Alfred\alfred.sqlite3`).

## Health checks

- `GET http://127.0.0.1:<port>/health` — 401 without the runtime token in production mode.
- The port is dynamic per launch; in dev it is fixed at 8765.

## Related

- [[Development Setup]]
- [[Release Checklist]]
- [[Debugging]]

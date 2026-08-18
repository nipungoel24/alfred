---
type: operations
layer: meta
status: active
tags:
  - backend
---

# Running Alfred

## Development mode (two terminals)

1. Backend: `py -3 -m uvicorn app.main:app --host 127.0.0.1 --port 8765 --app-dir backend`
2. Frontend: `cd frontend; npm run dev`
3. Open `http://localhost:5173` — the Mail workspace is the landing page.
4. Connect Gmail ([[frontend.src.features.accounts.AccountsPage.AccountsPage|AccountsPage]]), Sync Now; analysis and All Mail backfill start on their own ([[Application Startup Flow]], [[All Mail Backfill Flow]]).

## Desktop mode

- Build the sidecar once ([[Building Backend Sidecar]]), then `npm run tauri dev` / the NSIS bundle ([[Windows Packaging]]).

## Health checks

- `GET http://127.0.0.1:8765/health` → `{status, ai}`.
- `GET /api/accounts` → per-account backfill status payload.
- `GET /api/emails/counts` → inbox/All Mail/category counts.

## Related

- [[Development Setup]]
- [[Release Checklist]]
- [[Debugging]]

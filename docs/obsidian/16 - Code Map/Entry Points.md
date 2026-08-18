---
type: architecture
layer: meta
status: active
tags:
  - architecture
  - critical-path
---

# Entry Points

The hands that open the system.

## Backend

- Process: `uvicorn app.main:app` (dev) / sidecar binary (desktop) → `app.main.lifespan`.
- Module entry: [[backend.app.main]] — the only module that starts workers.

## Frontend

- `frontend/src/main.tsx` → providers → [[frontend.src.App.App|App]] → Mail workspace (default page).

## Desktop

- `desktop/src-tauri/src/main.rs::main` → Tauri setup → sidecar spawn ([[Sidecar Architecture]]).

## Legacy (not runtime)

- `src/app.py` / `run_app.py` / `config/settings.py` — the pre-Alfred Streamlit/Groq prototype, retained for history only ([[Engineering Journal]]).

## Related

- [[Application Startup Flow]]
- [[Backend Code Map]]
- [[Frontend Code Map]]

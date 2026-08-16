# Alfred implementation report

## Final architecture

`React/Vite → localhost FastAPI → SQLite + Ollama`. The Tauri shell loads React. Raw email is normalized on import, persisted locally, fingerprinted, then analyzed once with Ollama. Cached structured analysis is condensed and synthesized by Ollama into the briefing; draft replies are lazy.

## Running Alfred

1. Install Ollama and run `ollama pull qwen3:4b`.
2. `python -m pip install -r backend/requirements.txt`
3. `python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8765`
4. In another terminal: `npm --prefix frontend install` then `npm --prefix frontend run dev`.

For a Windows desktop build, install Rust/Tauri prerequisites, run `npm --prefix frontend install`, then `cargo tauri build --manifest-path desktop/src-tauri/Cargo.toml`.

## Verification pass: bugs fixed

- The backend could not create a development database under sandboxed `%LOCALAPPDATA%`; verified development startup now uses `ALFRED_DATABASE_PATH` while production still defaults to `%LOCALAPPDATA%\\Alfred`.
- Added persistent inbox-briefing caching. Its fingerprint includes compact analysis payloads, model, and schema version, so importing/analyzing changed mail invalidates it without hashing raw bodies.
- Fixed mutable Pydantic collection defaults.
- Added malicious HTML normalization coverage; HTML is rendered as text in React, not injected as HTML.
- Fixed frontend TypeScript configuration and missing React typings. Added ESLint configuration and a frontend unit test.
- Added a deterministic PyInstaller sidecar build script and Tauri sidecar configuration/launch wiring.

## Verification results

- `python -m compileall backend`: passed (Python 3.12 executable was found outside PATH).
- `python -m pytest backend/tests -q --basetemp .pytest-tmp`: **4 passed**.
- FastAPI, started with `ALFRED_DATABASE_PATH=.runtime/alfred.sqlite3`: `/health` returned `{"status":"ok","ai":"unavailable"}`; `/api/config` returned the configured local model; CSV import persisted two normalized messages.
- `npm run lint`: passed.
- `npm test -- --run`: **1 passed**.
- `npm run build`: passed.
- Ollama 0.12.6 is installed, but `ollama serve` did not become responsive before timeout, therefore the real qwen3:4b smoke test was not passed or claimed.
- Cargo/Rust is not installed, therefore Tauri checks, desktop dev run, sidecar packaging, and Windows installer production build were not possible.

## Verification recorded in this environment

- `git diff --check -- .env.example backend frontend desktop docs` passed.
- Initial setup commands needed explicit executable paths because Python and Ollama are absent from PATH.
- `npm.cmd --prefix frontend …` did not work in this shell; running commands after `cd frontend` was verified.
- Creating a commit was blocked because this environment grants read-only access to `.git` and cannot create `index.lock`.

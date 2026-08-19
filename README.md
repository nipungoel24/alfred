# Alfred v0.1.0

**The Intelligent Inbox Protocol** — a local-first, Gmail-only smart inbox for Windows.

Alfred reads your Gmail mailbox, keeps a private local mirror, and runs a small local AI (Ollama + qwen3:4b) over it to produce executive intelligence: priorities, summaries, replies-needed, derived tasks, deadlines, and a daily briefing — in a premium Mattered-style three-pane desktop workspace.

> "I shall endeavor to filter the noise, sir."

## What Alfred does

- Gmail Desktop OAuth (system browser, PKCE) with DPAPI-encrypted tokens
- Real Gmail synchronization: initial, incremental (historyId), and progressive All Mail backfill
- Gmail categories (Primary / Promotions / Social / Updates / Forums) — never re-classified by the AI
- Inbox, All Mail, Overview, Important, Needs Reply, Tasks, Deadlines, Later, Accounts, Settings
- Local AI analysis: summary, priority, why-it-matters, needs-reply, deadlines, action items
- Local reply draft generation (no sending — read-only by design)
- Live SSE progress, virtualized inbox, light/dark themes

## Requirements (Windows)

- Windows 10/11 with WebView2 (preinstalled on modern Windows)
- [Ollama](https://ollama.com) running locally with the `qwen3:4b` model pulled (`ollama pull qwen3:4b`)
- A Google account (Gmail) and Gmail API credentials configured in the release build

## Installation

1. Run `Alfred_0.1.0_x64-setup.exe` (per-user install, no admin needed).
2. Launch Alfred from the Start Menu.
3. Connect your Gmail account (opens your default browser — OAuth never runs inside the app window).
4. Sync starts automatically; analysis and All Mail backfill run in the background.

## Privacy model

- Gmail data is fetched from Google (OAuth, read-only scope `gmail.readonly`).
- All AI processing happens locally through Ollama — mail text never leaves the machine for AI.
- SQLite data lives in your AppData (`%LOCALAPPDATA%\AlfredData\alfred.sqlite3`).
- OAuth tokens are encrypted with Windows DPAPI.
- Alfred does NOT send email, has no telemetry, and has no cloud AI fallback.

## Development

See the engineering knowledge base at `docs/obsidian/` (open as an Obsidian vault or plain Markdown):

- `docs/obsidian/Alfred - Home.md` — entry point
- `docs/obsidian/15 - Operations/Development Setup.md` — toolchain and run instructions
- `docs/obsidian/15 - Operations/Release Checklist.md` — packaging gates

Quick start:

```powershell
py -3 -m pip install -r requirements.txt
py -3 -m uvicorn app.main:app --host 127.0.0.1 --port 8765 --app-dir backend
cd frontend; npm install; npm run dev
```

## Known limitations (Round 1)

- Windows + Gmail only; no sending, no drafts in Gmail, no IMAP/Outlook.
- Ollama is an external prerequisite (install and start it yourself).
- The installer is currently **unsigned** — SmartScreen will warn until an Authenticode certificate is configured.
- The app icon is a generated placeholder pending the final brand asset.

> Historical note: an earlier Streamlit + LangGraph + Groq prototype remains under `src/`, `config/`, and `run_app.py` as legacy history — it is not part of the current product.

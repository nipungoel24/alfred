# Alfred

**A local-first Gmail command center for Windows.**

Alfred keeps a local mirror of your Gmail mailbox and uses a local Ollama model to help surface what matters: summaries, priority, replies needed, tasks, deadlines, search, and briefing-style views.

> [!WARNING]
> **Alpha / Preview software**
>
> Alfred is under active development and is **not production-ready or recommended for mission-critical use yet**. Breaking changes, migration changes, UI changes, and incorrect AI classifications are still possible. Back up your Alfred data before upgrading, review AI-derived tasks/deadlines against the source email, and use a non-critical/test Google account if you are evaluating the project for the first time.

## Project status

| Area | Current status |
| --- | --- |
| Platform | Windows 10/11, x64, Windows-first |
| Mail provider | Gmail |
| Gmail access | Read-only (`gmail.readonly`) |
| AI | Local Ollama, default model `qwen3:4b` |
| Local storage | SQLite |
| Multi-account | Supported |
| Public binary release | **Not published yet** |
| Installer signing | **Unsigned preview build** |
| Stability | **Alpha / active development** |

There are currently **no official GitHub Release assets** for Alfred. Until a signed/public release is published, the supported way for an external tester to obtain the current app is to **build the Windows installer from source** using the instructions below.

## What Alfred currently does

- Connects one or more Gmail accounts through Google OAuth + PKCE.
- Synchronizes Inbox, archived mail, sent mail, Gmail categories, and progressive All Mail history.
- Stores a local SQLite mailbox cache on your Windows machine.
- Runs email analysis locally through Ollama.
- Produces summaries, priority, reasons for priority, reply-needed signals, tasks, and deadlines.
- Provides SQLite FTS5/BM25 full-text search plus structured filters such as `from:`, `subject:`, `is:unread`, `is:important`, and `in:inbox`.
- Lets you inspect the exact source email behind a task/deadline.
- Lets you mark a false detection as **Not a task** so it does not reappear during normal re-derivation.
- Lets you manually override a task's priority.
- Provides resizable Mail / Reader / Intelligence panes with persisted layout.
- Opens safe `http`, `https`, `mailto`, and `tel` links through the system application.
- Generates reply suggestions locally, but does **not** send email.

## Before you install

### For a future packaged release

When an official release is eventually published, installation should be as simple as downloading the Windows installer, running it, installing Ollama, and connecting Gmail.

That public distribution path is **not ready yet**. The repository currently has no published GitHub Release installer, and preview installers are unsigned.

### For the current alpha

To build Alfred yourself you need:

- Windows 10/11 x64.
- Git.
- Python 3.12+ (3.12 is the recommended baseline for this project).
- Node.js 22+ and npm.
- Rust stable + the Windows/Tauri build prerequisites (Microsoft C++ Build Tools and WebView2 tooling).
- Tauri CLI 2.
- Ollama for Windows.
- Your own Google OAuth **Desktop app** client ID for Gmail access.

For the Windows/Rust prerequisites, follow the Tauri 2 Windows prerequisites: <https://v2.tauri.app/start/prerequisites/>

---

# Install the current alpha from source

The steps below are PowerShell commands and should be run from a normal Windows user account unless a prerequisite installer asks for elevation.

## 1. Clone Alfred

```powershell
git clone https://github.com/nipungoel24/alfred.git
cd alfred
```

If you are evaluating an unreleased branch or commit, switch to that exact branch/commit **before** building it:

```powershell
git switch <branch-name>
```

Do not mix binaries built from one commit with a source tree from another commit when debugging.

## 2. Install and prepare Ollama

Install Ollama for Windows from <https://ollama.com/download/windows>, then pull Alfred's default model:

```powershell
ollama pull qwen3:4b
```

Check that the model is available:

```powershell
ollama list
```

If Ollama is not already running, start it:

```powershell
ollama serve
```

Alfred can still open when local AI is unavailable, but AI analysis/drafting will remain paused until Ollama and the configured model are available.

## 3. Create your Google OAuth credentials

Alfred currently expects each source builder/tester to provide their own Google OAuth credentials.

1. Open Google Cloud Console.
2. Create/select a project.
3. Enable the **Gmail API**.
4. Configure the OAuth consent screen for your project.
5. Create an OAuth client of type **Desktop app**.
6. If your consent screen is still in testing mode, add the Gmail account(s) you intend to test as test users.
7. Copy the OAuth client ID. If Google supplied a client secret, copy that as well.

Alfred currently requests:

- `https://www.googleapis.com/auth/userinfo.email`
- `https://www.googleapis.com/auth/gmail.readonly`

It does not request Gmail send/modify scope.

## 4. Configure the backend

Create the development configuration file in **`backend/.env`**:

```powershell
Copy-Item .env.example backend\.env
notepad backend\.env
```

Set at least:

```dotenv
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen3:4b
ALFRED_HOST=127.0.0.1
ALFRED_PORT=8765
GMAIL_CLIENT_ID=YOUR_GOOGLE_DESKTOP_CLIENT_ID
GMAIL_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET_IF_PROVIDED
```

`GMAIL_CLIENT_ID` is required for Gmail OAuth. `GMAIL_CLIENT_SECRET` may be left empty when your Google Desktop client does not require/provide one.

Do **not** commit `backend/.env` or real OAuth credentials.

> [!IMPORTANT]
> Source-development mode reads `backend/.env`. Packaged builds do not depend on that source file after installation: `backend/build_sidecar.py` stages the release configuration into the packaged backend sidecar. If you change OAuth/Ollama configuration for a packaged build, rebuild the sidecar and installer.

## 5. Install Python dependencies

Create a virtual environment from the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
```

The current sidecar builder can optionally use `python-dotenv` to read `backend/.env` while packaging. Install it before building an installer:

```powershell
python -m pip install python-dotenv
```

Do **not** use the repository-root `requirements.txt` for the modern Alfred application; it belongs to the legacy Streamlit prototype. The current FastAPI backend dependencies are in `backend/requirements.txt`.

## 6. Install frontend dependencies

```powershell
npm --prefix frontend ci
```

## 7. Install the Rust/Tauri toolchain

Install Rust stable using <https://rustup.rs/> and complete the Tauri Windows prerequisites linked above.

Then install Tauri CLI 2 if `cargo tauri --version` is not already available:

```powershell
cargo install tauri-cli --version "^2.0.0" --locked
```

Verify:

```powershell
rustc --version
cargo --version
cargo tauri --version
```

## 8. Build the packaged FastAPI sidecar

From the repository root, with the Python virtual environment active:

```powershell
python backend\build_sidecar.py
```

The build should create the target-suffixed backend executable under:

```text
desktop\src-tauri\binaries\
```

If the builder warns that `GMAIL_CLIENT_ID` is missing, **stop** and fix your configuration before creating the installer. A build without a configured Gmail client ID cannot start Google OAuth.

## 9. Build the Windows installer

```powershell
cd desktop\src-tauri
cargo tauri build
```

Tauri automatically builds the frontend before packaging. With the current NSIS configuration, the installer is generated under the Tauri release bundle directory, normally:

```text
desktop\src-tauri\target\release\bundle\nsis\
```

The current package name is similar to:

```text
Alfred_0.1.0_x64-setup.exe
```

## 10. Install Alfred

Run the generated NSIS installer.

The current build uses a **per-user** installation, so Alfred is installed under the current Windows profile rather than system-wide.

> [!NOTE]
> The preview installer is currently unsigned. Windows SmartScreen may warn about an unknown publisher. Do not bypass security warnings for binaries you did not build yourself or obtain from a source you trust.

## 11. First launch

1. Make sure Ollama is available and `qwen3:4b` is installed.
2. Launch **Alfred** from the Windows Start Menu.
3. Open **Accounts**.
4. Choose **Connect Gmail** / **Add another Gmail account**.
5. Your default browser opens Google's OAuth flow.
6. Select the Gmail account and grant the requested read-only permissions.
7. Return to Alfred after Google reports that the connection completed.
8. Allow the initial Inbox sync, All Mail backfill, and local analysis queue to run.

You can continue using the mailbox while AI analysis is processing. Alfred reports local AI state in the UI instead of treating Ollama availability as application startup readiness.

---

# Using Alfred

## Mail

- Use **Inbox** for active inbox mail and Gmail category tabs.
- Use **All Mail** for inbox + archived + sent mail.
- Use the account selector to view one Gmail account or all connected accounts.
- Drag the pane separators to resize Mail, Reader, and Intelligence.
- Alfred remembers a valid pane layout locally.

## Search

The main search box performs local full-text search using SQLite FTS5/BM25.

Examples:

```text
invoice
from:alice@example.com
subject:"quarterly report"
is:unread
is:important
is:reply
in:inbox
in:archived
in:sent
in:all
```

Search is local to the mailbox data Alfred has already synchronized.

## Tasks and deadlines

Tasks and deadlines are AI-derived and can be wrong.

For any derived item:

- choose **View email** to inspect the exact source message;
- use **Open in Mail** for the full mail workspace;
- change a task's priority manually when Alfred got it wrong;
- choose **Not a task** when an email was incorrectly interpreted as containing a task.

A **Not a task** decision is stored as a durable dismissal so normal task rebuilding does not simply recreate the rejected task.

## Local AI

The default model is `qwen3:4b` through Ollama at `http://127.0.0.1:11434`.

If Ollama stops, Alfred's mailbox remains usable. AI work pauses and resumes after local AI becomes healthy again.

---

# Privacy and data model

Alfred is local-first, **not network-free**.

- Gmail synchronization communicates with Google's Gmail/OAuth APIs.
- AI analysis and drafting use the locally configured Ollama endpoint; the current application has no cloud-AI fallback.
- Gmail OAuth tokens are stored encrypted with Windows DPAPI.
- Alfred's SQLite data is stored by default at:

```text
%LOCALAPPDATA%\AlfredData\alfred.sqlite3
```

Older installations may still use:

```text
%LOCALAPPDATA%\Alfred\alfred.sqlite3
```

Desktop startup diagnostics are written to:

```text
%LOCALAPPDATA%\AlfredData\logs\desktop.log
```

Before testing an upgrade that changes local storage/migrations, make a backup of your Alfred data.

---

# Run Alfred in development mode

For browser-based development, run the backend and frontend in separate PowerShell terminals.

Backend from the repository root:

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8765 --app-dir backend
```

Frontend:

```powershell
npm --prefix frontend run dev
```

The frontend development server runs at `http://localhost:5173`.

For the native Tauri development window, build the backend sidecar first, then:

```powershell
cd desktop\src-tauri
cargo tauri dev
```

---

# Tests and quality checks

Backend:

```powershell
python -m pytest backend\tests -q
```

Frontend:

```powershell
npm --prefix frontend test
npm --prefix frontend run lint
npm --prefix frontend run build
```

Rust/Tauri:

```powershell
cd desktop\src-tauri
cargo fmt --check
cargo clippy
cargo test
```

The repository currently does **not** enforce these gates through protected GitHub CI status checks, so contributors should run them locally before proposing changes.

---

# Troubleshooting

## Alfred says Local AI is offline / unavailable

Check Ollama:

```powershell
ollama list
ollama pull qwen3:4b
ollama serve
```

Then use Alfred's **Retry** action or allow the local AI supervisor to recover automatically.

## Gmail connection says OAuth credentials are not configured

Check `backend/.env` and make sure `GMAIL_CLIENT_ID` is not the placeholder value.

If you are running an installed build, changing the source `.env` after packaging is not enough. Re-run:

```powershell
python backend\build_sidecar.py
cd desktop\src-tauri
cargo tauri build
```

Then reinstall the new build.

## Alfred does not start correctly after installation

Inspect:

```text
%LOCALAPPDATA%\AlfredData\logs\desktop.log
```

When reporting a problem, include the Alfred build ID from **Settings → About** and sanitized startup/error lines. Do not post OAuth tokens, credentials, private email bodies, or your SQLite database publicly.

## Search does not find an expected message

Alfred searches its **local synchronized cache**. Confirm the relevant account/history has finished syncing or backfilling before treating a missing result as a search-engine bug.

---

# Current alpha limitations

- Windows + Gmail only.
- No Gmail sending/modification; Alfred currently uses read-only Gmail access.
- Ollama is an external prerequisite for AI features.
- Local-model classifications, tasks, deadlines, and drafts can be wrong; always verify important output against the source message.
- The public installer/update/signing pipeline is not complete.
- No official GitHub Release binary is currently published.
- Preview installers are unsigned.
- Repository CI is not yet enforced as a required merge gate.
- Public OAuth/distribution onboarding still needs hardening before Alfred should be presented as production-ready software.

## What should happen before a public production release

At minimum, Alfred should have:

- a reproducible GitHub release workflow;
- required CI checks and branch protection;
- Authenticode/code signing for Windows releases;
- a deliberate Google OAuth production/verification strategy;
- tested installer upgrade/uninstall behavior across clean machines;
- documented backup/recovery and data migration policy;
- public security/privacy documentation and issue-reporting process;
- broader real-world testing across Windows machines, Gmail accounts, mailbox sizes, and failure scenarios.

---

# Repository notes

The modern product lives primarily in:

```text
backend/             FastAPI backend, Gmail integration, SQLite, local AI
frontend/            React + TypeScript + Vite desktop UI
desktop/src-tauri/   Tauri/Rust Windows shell and installer configuration
docs/obsidian/       Engineering knowledge base
```

An earlier Streamlit/LangGraph prototype remains in legacy paths in the repository for historical reference. Do not use the root legacy `requirements.txt` as the dependency file for the modern application.

---

## Contributing / testing

Alfred is still a preview project. If you test it, useful bug reports include:

- the Alfred build ID from **Settings → About**;
- Windows version;
- whether the problem occurred in an installed build or development mode;
- the relevant feature (startup, Gmail sync, search, AI, tasks, resizing, etc.);
- sanitized logs/error text and clear reproduction steps.

Never attach OAuth tokens, credentials, raw private email content, or your live Alfred SQLite database to a public issue.

# Alfred — Phase 1 Visual QA Record

Date: 2026-09-27
Branch: `feature/mail-workspace-productization-20260907`
Baseline commit: `eb18331` — `fix(alfred): polish phase 1 visual regressions`

First pass record kept below in *Superseded findings*; this is the second, far more
complete pass. Every claim here is tied to something that was actually observed.

---

## Environment

| | |
| --- | --- |
| OS | Windows 11 Home Single Language, build 26200 |
| Display | 3840×2160 physical, 2560×1440 logical (**150% scaling**) |
| Session | Interactive desktop, **actively in use by the operator** (see *Capture hazards*) |
| App execution mode | **Installed application.** NSIS `currentUser` installer run with `/S` (exit 0) over the previous install; app launched from `%LOCALAPPDATA%\Alfred\alfred-desktop.exe` |
| Data | A **real connected Gmail account** (982 inbox / 1068 all mail, real correspondents). Nothing mocked. |
| Theme | Light **and** dark |
| Log | `%LOCALAPPDATA%\AlfredData\logs\desktop.log` |

Artifacts live under `%TEMP%\opencode\qa\` and are intentionally **not** committed —
they contain real mailbox content.

---

## Release packaging (the blocker from the first pass)

The first pass never got past "the installer exists". This pass installed and ran it.

**The installed build was stale.** `%LOCALAPPDATA%\Alfred` held a **10 Sep** shell *and*
sidecar, while four backend sources — `app/mail/secure_store.py`, `app/config.py`,
`app/main.py`, `build_sidecar.py` — were newer. Shipping that would have omitted the
current DPAPI credential handling. Rebuilt before any conclusion was drawn.

| | Before | After |
| --- | --- | --- |
| `alfred-backend.exe` | 37.6 MB, 10 Sep | 24.5 MB, rebuilt from current source |
| `alfred-desktop.exe` | 11.3 MB, 10 Sep | 11.4 MB, rebuilt |
| `alfred.sqlite3` | 14.6 MB, 27 Sep 11:54 | **unchanged** — user data preserved across install |

Build sequence, both steps required:

1. `py -3.12 backend/build_sidecar.py` — rebuilds the PyInstaller sidecar. PyInstaller
   was not installed in this interpreter and had to be added.
2. `cargo tauri build` from `desktop/` — embeds `frontend/dist` and packages the sidecar.

`build_sidecar.py` **refuses to run** when `GMAIL_CLIENT_SECRET` is set (ADR-010). The
variable is read from `backend/.env` via `load_dotenv`, so clearing it in the shell is
not enough — it is reloaded. Building without touching `backend/.env` required setting
the key to a *present but empty* value so `load_dotenv(override=False)` skips it and the
guard's truthiness check passes.

Verified after the rebuild: `production.env` contains only `GMAIL_CLIENT_ID` — no
`GMAIL_CLIENT_SECRET`, `GOOGLE_CLIENT_SECRET`, `SECRET`, `PRIVATE_KEY` or
`REFRESH_TOKEN`. The release secret scan passes, with the tool's own standing caveat
that a byte scan cannot see inside a compressed PyInstaller archive.

---

## Confirmed issues, and what was done

### B1 — Sidebar lit two items at once, and the real page was never lit (severity: high) — FIXED

Reproduced on Overview, Deadlines, Settings and Accounts. Two rows carried the active
treatment (teal left bar + tint) simultaneously: the page you were on, *and* a mail row.

Cause: `App.tsx:184` builds `activeMailView` as `` `${mailScope}:${mailFilter}` ``, which
is **always truthy**, and `handleNavigate` never resets it. `IconRail.tsx:110` then read
`!(item.page === 'overview' && activeMailView)` — permanently false — so the Overview row
could never be active, and a mail row stayed lit from a stale view on every other page.

Fix: a mail item is now active only when `page === 'mail'`, and a page item is active on
its own page. Two regression tests added, one iterating all five non-mail pages and
asserting exactly one `aria-current="page"` carrying the right label.

### B2 — ~1.2 s blank white frame before the boot shell (severity: medium) — FIXED

First launch, measured:

| t | Observed |
| --- | --- |
| +1.22 s | Window up, correct title bar and icon, **content area pure white** |
| +2.89 s | Branded boot shell: logo tile, "Starting Alfred", "Preparing your workspace.", staged steps, indeterminate bar |

`tauri.conf.json` set `visible: true` with no background, so the window showed before the
webview painted its first frame. Added `"backgroundColor": "#0b0d13"`, the dark `--bg-app`
canvas. Re-verified: the **first** observable frame is now the fully rendered dark boot
shell, no white interval.

*(A light-theme user now sees a brief dark frame instead of a white one. Strictly better,
but the flash is not eliminated for them; eliminating it entirely needs a hidden-until-
painted window, which was out of scope here.)*

### B3 — Raw HTML entities in message snippets (severity: medium) — FIXED AT INGESTION

> `Hi Goel, We hope this message finds you well. We&#39;ve received your …`

`gmail.py` took `detail.get("snippet")` raw while `subject` came straight from headers;
both arrive HTML-escaped from Gmail. `normalize_text()` already unescapes, but only on the
**import** path — the Gmail sync path constructs `Email` directly and bypassed it.
Now unescaped at the point of ingestion.

**Residual, stated plainly:** messages already in SQLite keep their stored snippet, so
`&#39;` is still visible on the existing backlog until those messages are re-fetched.
Verified still present in the list after the fix, as expected. Fixing the display instead
of the ingest would have hidden the defect rather than removed it.

### B4 — The sidecar exit code was redacted out of the log (severity: low) — FIXED

Every log line passes through a global redaction filter (`main.rs:906`) that treats a
bare `code=` as an OAuth authorization code. The supervisor logged
`sidecar.exited pid=… code=Some(0)`, so the process exit status — the single most useful
value when a sidecar dies — was logged as `code=[redacted]` on every occurrence. Field
renamed to `exit=`, which cannot collide with the OAuth rule. Redaction logic untouched.

---

## What was actually inspected

Against the **installed** app, real mailbox, both themes:

- **Startup**: window at +1.22 s, boot shell at +2.89 s, then the working UI. No second
  launch required. No console/terminal window. No hang.
- **Mail view**: category tabs `Primary 80 / Promotions 77 / Social 2 / Updates 823 /
  Forums 0`; *All mail synced*; quick filters; *Filter inbox*; message rows with sender,
  subject, snippet, `IMPORTANT`/`REPLY` badges, date, teal unread bar on the selected row;
  empty reader state ("Select a message to read it."); `Analyzing 307 messages` progress.
- **Overview**: greeting, `982 messages in Inbox · 1068 in All Mail`, four stat tiles,
  *Needs attention* list with `HIGH`/`REPLY` badges, *Upcoming*, footer status.
- **Deadlines**: `0 upcoming` with skeleton rows still showing in the captured frame.
- **Settings**: Theme `System / Light / Dark` segmented control; Local AI block
  (`qwen3:4b`, `Ollama (local)`, Ready, installed/running Yes, `307 pending · running`);
  Data block (`Local SQLite (AppData)`, **`Encrypted with DPAPI`** — confirms the rebuilt
  sidecar's credential path works); Privacy block.
- **Accounts**: connected Gmail account, provider, status, last sync, older-mail state,
  *Sync now* / *Disconnect* / *Add another Gmail account*.
- **Dark mode**: toggled via Settings and re-inspected Mail, Accounts, Overview. Surfaces,
  borders, muted text and the teal accent all hold up; no unreadable or inverted pair seen.
- **Shutdown**: `desktop.exit_requested` → `POST /api/shutdown` (200) →
  `shutdown.graceful_requested delivered=true` → `shutdown.exited_cleanly`. Afterwards
  **0** `alfred-desktop`, **0** `alfred-backend`, and **0** WebView2 children (the 25
  `msedgewebview2` processes on the machine belong to Windows, DriveFS, WhatsApp and
  meetily). No orphans.

---

## Capture hazards (why some frames were discarded)

Both cost real time and both produced convincing false findings. Recording them so the
next pass does not repeat them.

1. **A Chrome window kept covering Alfred.** Alfred's window had migrated to a secondary
   monitor at `-1929,-9` and a topmost Chrome window painted over it. `CopyFromScreen`
   captured Chrome. This produced an entirely false "unconstrained image overflowing the
   reader and covering the sidebar" finding — the "image" was a product page in the
   operator's browser, and the "unresponsive navigation" was my clicks landing on Chrome.
   **That finding is retracted in full.** It was an automation artifact, not a defect;
   the reader renders plain text through `LinkifiedBody` and has no HTML image path.
   Mitigation used afterwards: `PrintWindow` with `PW_RENDERFULLCONTENT`, which renders
   the target window's own surface and is immune to occlusion, plus a brightness check
   that rejects uniformly black frames. `PrintWindow` is not sufficient alone — it
   intermittently returns an all-black frame, which is why the retry-and-reject loop
   exists.
2. **The app appeared to quit by itself, twice.** Both times `desktop.exit_requested`
   appeared with no error and a clean shutdown. It was not an app fault: the process was
   being reaped at my own tool-call boundaries. Running launch + tour inside a *single*
   invocation kept the app alive for the whole tour. There is no idle timer or watchdog in
   `main.rs` that exits, and `/health` was still 200 immediately before each exit.
3. **DPI-unaware capture** (from the first pass) produced black bands and duplicated
   panes that looked like a severe layout bug. Artifact only; after per-monitor v2
   awareness the bands vanished. Not a defect.

`MoveWindow` also repeatedly collapsed the window to 199×34, and UI Automation found 0
buttons (the WebView2 tree is not exposed), so navigation was driven by mouse input
against verified coordinates.

---

## What was NOT inspected

No claim is made about any of this.

- **The reading pane with a message open.** The reader's *empty* state was seen on every
  capture; a message was never successfully opened in a verified frame. The earlier
  apparent "opened reader" was the Chrome artifact above. Subject, From/To/Date grid, the
  68ch measure, attachments and the action row remain **unverified on screen**.
- **The intelligence panel with real content** — never opened. The borders, radius and
  separation restored by the dead-CSS gate are still unverified.
- **The Tasks page** — my click at the recorded y landed on Deadlines, so Tasks content
  was never seen.
- **Error, empty, retry, AI-unavailable, syncing and authentication-required states** —
  not triggered. (AI-unavailable appeared incidentally as `Local AI offline` /
  `AI recovering` during a model reload, which is the one such state actually seen.)
- **Window sizes.** Every capture is the same size. The 1100 px rail collapse, the 900 px
  intelligence padding compression, and degradation below the 900 px `minWidth` are all
  **unverified**.
- **Post-fix on-device confirmation of B1.** The rail fix is covered by a deterministic
  unit test across all five non-mail pages, which is stronger evidence than a screenshot,
  but the operator's active Chrome usage kept stealing foreground and the post-fix
  navigation clicks did not land. The fix is verified by test, not by eye.
- **Keyboard behaviour** — Ctrl+K, skip link, arrow navigation, Enter-to-open were
  verified by the UI-10 tests, not by eye.

### Open question, not yet a defect

Deadlines reported `0 upcoming` while skeleton rows were still on screen in the captured
frame. That is consistent with a load in progress, but it was not re-checked after the
list settled, so whether the empty state replaces the skeleton promptly is **unresolved**.

---

## Deferred

| Item | Why deferred | Intended task |
| --- | --- | --- |
| Reader with a message open | Never seen in a verified frame | Repeat this gate |
| Intelligence panel content | Never opened | Repeat this gate |
| Tasks page content | Click landed on Deadlines | Repeat this gate |
| Window sizes 1100/1000/900/800 | No reliable resize automation | Repeat on a 100%-scale display, ideally unattended |
| Error / retry / AI-unavailable states | Not triggered | Repeat with a deliberately failing backend |
| Deadlines empty state timing | Unresolved | Recheck after load settles |
| Backlog snippets still show `&#39;` | Stored before the B3 fix | Clears as messages are re-fetched |
| `cargo build --release` serves no frontend | Build-invocation trap, not a code defect | Repo docs |
| Message list not keyboard navigable | Interaction-model change, out of scope | Dedicated listbox task |
| AI-state vocabulary consolidation (4) | Not visually problematic | Cleanup task |
| Intelligence off-scale values (`6px 0`, `3px`) | Panel never rendered | Needs the panel open first |
| Remaining inline `style` objects | Not visually problematic where seen | Cleanup task |
| `Ctrl+1..6` and `?` overlay | Not started | Keyboard shortcut task |
| Real brand assets | Placeholder purple "A" tile | Branding task |
| 3.2 s looping status pulse | Not observed as distracting | UI-11 motion decision |
| `.section-label` 10px / 0.09em vs spec 10.5px / 0.04em | Read acceptably at real size | Separate typography decision |
| `.badge-reply` accent | Rendered teal, legible, not garish | Design decision |
| `#f28b82` fallbacks | Never paint | Cleanup task |

---

## Superseded findings (from the first pass)

- **A1 — release build did not compile.** Fixed in `eb18331`; `cargo tauri build` succeeds
  and the installer is produced. Still valid.
- **A2 — bare `cargo build --release` serves no frontend.** Still valid; the shipping
  command is `cargo tauri build` from `desktop/`.
- **A3 — snippet HTML entities.** Superseded by **B3**, which fixed it at ingestion and
  identified the real cause (the sync path bypassed `normalize_text`). A3's guess that it
  "belongs in the Gmail normaliser" was right, but for a more specific reason.
- **False finding, retracted:** "reader shows a full-bleed unconstrained image covering
  the whole window". Chrome occlusion. Not a defect.

---

## Manual verification

**What was done:** rebuilt the sidecar and the bundle, installed the NSIS artifact over
the existing install (mailbox database verified untouched), launched the installed app,
and inspected the real UI across both themes with a real mailbox — plus a full clean
shutdown with a process and log audit.

**What was not done:** open a message, visit Tasks, open the intelligence panel, resize
the window, or trigger error states.

**Status:**

- Automated verification: **PASS** — 657 tests, 0 failures. (Frontend runner reports 31/31
  files passing but exits non-zero on a pre-existing unhandled `boom` rejection in
  `focus.retry.test.tsx`, a file untouched by this work.)
- Manual visual verification: **PARTIAL** — installed app, real mailbox, both themes, one
  window size. Reader-with-message, intelligence panel, Tasks and all size breakpoints
  still unverified.
- Gate 1 packaged-app verification: **PASS on lifecycle and packaging** — installed from
  the NSIS artifact, launched once, no white frame, no second launch, no terminal, clean
  graceful shutdown, zero orphan processes, `desktop.log` reviewed. **The gate is not
  fully PASS** because the reader-with-message, intelligence panel, Tasks and
  multiple-size checks remain outstanding.

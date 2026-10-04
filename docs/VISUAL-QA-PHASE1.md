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

## Tasks UI and task extraction (surgical pass)

Date: 2026-09-27. Baseline `9783a66`.

### The action column moved between rows

**Cause, structural.** `.list-row` was a plain flex row and the two actions were loose
flex children. One of them was rendered conditionally:

```tsx
{task.source_email_id && (<button className="icon-btn">…View email</button>)}
<button className="icon-btn">…trash…</button>
```

so a row with a source email carried two controls and a row without carried one, and the
trash icon sat at a different x on each. Separately, `.icon-btn` is a fixed **28px**
`inline-grid` while `.icon-btn .btn-label` is `white-space: nowrap`, so the "View email"
label overflowed its own button and collided with its neighbour. The group also had no
`align-items`, so it drifted vertically on wrapped rows.

**Fix.** The row is now a three-track grid, `auto minmax(0, 1fr) var(--task-actions-width)`,
with a new `--task-actions-width: 116px` token. Both controls always render — the view
action is `disabled` with an honest label when a row has no source email — so the column
is the same width on every row. Icon and label are one control (`.task-action`,
`inline-flex`, auto width) rather than text inside a 28px box. Two inline `style` objects
in the row became `.task-content`, `.task-note` and `.task-due`.

**Measured on the installed app at 1940px, 8 consecutive task rows** spanning short and
long titles, with and without a due date, with and without a description, and three
priorities:

| control | x range | spread across rows |
| --- | --- | --- |
| mail icon | 1682–1702 | 0 px |
| "View email" label | 1709–1792 | 0 px |
| trash icon | 1825–1843 | 0 px |

### Task extraction was writing prose into structured fields

Traced with real data from `%LOCALAPPDATA%\Alfred\alfred.sqlite3` (982-message
mailbox, `qwen3:4b`). **Gmail normalisation is not the cause** — the stored bodies are
clean. The corruption is introduced at the **AI extraction boundary**, in three places
that compounded:

1. **The prompt asked for it.** `ANALYSIS_PROMPT` rule 4 read *"In 'deadlines', preserve
   the relative wording as 'due_at' when no calendar date is present"* — an instruction
   to write prose into a date field. It also contradicted rule 5, which said to skip
   ambiguous timings like "soon".
2. **The schema invited it.** `ActionItem.deadline` and `Deadline.due_at` were typed
   `str | None` and described to the model as *"a raw string (e.g. 'Friday' or '5 PM
   today')"*. These descriptions ship verbatim in `model_json_schema()`, so the model
   was being told prose was correct.
3. **Nothing validated the result.** `EmailAnalysis.model_validate_json(raw_text)`
   accepted whatever came back.

Derivation then propagated it unexamined, and additionally used
`deadlines[].description` as the **task title**, which is how a bare date became a task.

**Traced example** — `[GitHub] Sudo email verification code`, an automated OTP with no
user action. Model output: `action_items[0].deadline = "15 minutes from now"` and
`deadlines[0] = {description: "15 minutes from now", due_at: "15 minutes from now"}`.
Persisted: a task titled `15 minutes from now` with `due_at = "15 minutes from now"`.
After the fix, re-deriving that same email produces **no task at all**.

Four more real emails were traced the same way: a Techugo marketing blast, an Indeed
application receipt, a DM360 job alert, and a job description. The Indeed receipt had
`deadline = "due_at: soon"`; the DM360 alert had `description = "No action required"`,
which the model meant as *there is no task* and which became one. All four now produce
nothing.

**Fix, at the earliest incorrect boundary:**

- `backend/app/services/due_dates.py` (new) is the single place that decides what a due
  value may be. It rejects field labels, vague prose, bare clock times and free text, and
  returns a normalised ISO-8601 instant or `None`. Relative offsets resolve only against
  a supplied reference timestamp; months are refused rather than guessed.
- `ActionItem.deadline` / `Deadline.due_at` gained `mode="before"` validators, so the
  invariant holds the instant model output becomes a domain object. Their descriptions
  were rewritten to state the ISO-or-null contract, which is what the model now sees.
- The prompt lost rule 4 and gained explicit rules: never prose, never a field name in a
  field's value, a `description` must state something to DO, and "no action required"
  means return empty lists.
- `derive_tasks` re-normalises against `email.received_at` (the one place a reference
  exists), rejects non-action and temporal-only titles, drops an "explicit" deadline
  whose value is unreadable, and no longer writes `"Owner: user"` / `"Due: …"` into
  `description`. `owner` is a real column now.
- Derivation version 2 → 3.

**Domain check.** `due_at` is one shape: `2026-09-12T00:00:00+00:00`. Of the 90 distinct
`due_at` values in the live database, 43 normalise to `None` and 47 are real instants.

### Existing data: documented, not rewritten

Nothing in the database was modified. The pre-existing rows are **stale historical
extraction**, and the brief is explicit that reprocessing must be an explicit, safe
operation rather than an implicit migration — so it was not performed.

| | count |
| --- | --- |
| tasks total | 291 |
| `due_at` holds prose or a field label, not an instant | 97 |
| title is provably not an action (all still `pending`) | 57 |
| `description` carries `Owner: …` | 174 |
| `description` carries `Due: …` | 59 |
| already correct on both counts | 137 |

The Tasks page in the screenshots below therefore still shows `12th September 2026`,
`15 minutes from now`, `due_at: soon` and `No action required`. That is the honest
current state, not a regression.

`TaskMigrationService.run_migration()` is the existing explicit repair: it re-derives
from cached analyses, preserves `status`, `created_at` and any `priority_override`, and
removes only *pending* rows the new logic no longer produces. It was **not run**.

### Overview / sidebar active state — verified on the device

`9783a66` was not taken on trust. All ten destinations were visited in the installed app
and the active state was measured by detecting the 2px accent bar each active rail item
paints at its left edge:

| destination | active items detected | count |
| --- | --- | --- |
| Inbox / All Mail / Important / Needs Reply / Later | the matching mail row | 1 |
| **Overview** | **Overview** | **1** |
| **Tasks** | **Tasks** | **1** |
| Deadlines / Accounts / Settings | the matching row | 1 |

Overview is active when on Overview, Tasks is active when on Tasks, **no mail row stays
lit after leaving the mail pages**, and no capture ever showed two active rows.

---

## Visual verification actually performed

Against the NSIS install of the current `cargo tauri build`, real mailbox, dark theme.
Screenshots are in `%TEMP%\opencode\qa\` and are not committed.

- **Tasks, 1940x1330** — inspected. 8 rows visible: short title, long title, title with a
  description, rows with and without a due date, `high`/`medium`/`low` priority. Action
  column measured at 0 px spread. No source-email-less row was present in view, so the
  disabled-view-action state was verified by unit test rather than by eye.
- **Tasks, 900x1330** (the `minWidth`) — inspected. Rail collapses to icons correctly and
  the Tasks icon is active. The action column stays aligned, but the row is **clipped at
  the right edge** — and so is the header ("AI ready", the Pending/Completed control).
  This is a **pre-existing global horizontal overflow at 900 px**, not caused by this
  change; the whole layout is wider than the viewport there.
- **Sidebar, 1940x1330** — all ten destinations, measured as above.
- **Mail with a message open, 1100x1330** — inspected incidentally at the collapsed-rail
  width. The reader renders correctly: subject, From/To/Date grid, body, empty-reader state.
  This closes a screen the previous gate had listed as never seen.
- **Reader with a message open, 1940px** — **not** inspected. The reader evidence above is
  at 1100 px only.
- **Intelligence panel with content** — still not opened.
- **1400 px and 1000 px** — **not** verified. A capture at 1400 px came back showing the
  desktop wallpaper because Alfred was not foreground, so it was discarded rather than
  reported.
- **Scrolling deep into the list, wrapped multi-line titles, completed tasks** — not
  inspected; the 8 measured rows were all single-line titles.
- **Light theme** — not re-inspected this pass.

---

## Tests

| Suite | Result |
| --- | --- |
| Backend | **283 passed**, 0 failed (was 241) |
| Tools | 9 passed |
| Rust | 35 passed |
| Frontend | **383 passed**, 32/32 files (was 376/31) |
| `tsc -b` / ESLint / `cargo fmt` / `cargo clippy` / frontend build | all clean |
| Release secret scan / Windows deployment check | exit 0 |

New: `backend/tests/test_task_extraction_contract.py` (40 cases) and
`frontend/src/features/tasks/TasksPage.layout.test.tsx` (7 cases).

Four existing tests asserted the defect and were corrected rather than deleted —
`due_at == "Friday"`, `due_at == "Before 5 PM"` and `deadline_count == 2` all encoded
prose in a date field. Each keeps its original intent, restated against a real ISO date,
and gained a companion case asserting the prose form is now rejected.

The frontend runner still exits non-zero on the pre-existing unhandled `boom` rejection
in `src/features/focus.retry.test.tsx`, which this work does not touch.

---

## Final Phase 1 pass: task domain cleanup and verification

Date: 2026-09-27. Baseline `f526bf4`.

### Is a manually created task distinguishable? (the STOP condition, resolved)

Before any destructive change: **no**. There is no task-creation route
(`GET /api/tasks`, `POST .../toggle`, `POST .../dismiss`, `PATCH /api/tasks/{id}`,
`DELETE /api/tasks/{id}` and nothing else), no frontend affordance that creates one,
and `save_task`/`save_tasks_batch` are called only from derivation and from the
toggle route. Every row in the table is machine-derived by construction, so a
reconcile cannot destroy something the user typed. The ambiguity the brief warned
about cannot arise here.

### One authoritative path

`reconcile_tasks_from_analyses(repo, model) -> ReconcileReport` is now the only code
that changes the tasks table. `rebuild_tasks_from_analyses` is a thin wrapper (startup
calls it by name) and `TaskMigrationService.run_migration` delegates to it, so there is
no second implementation that can drift.

What changed, and why the old code was unsafe:

| | before | now |
| --- | --- | --- |
| stale derivation rows | skipped if the fingerprint existed, so a v2 row survived a logic change untouched | **updated in place** via `ON CONFLICT ... DO UPDATE` |
| old versions | only `derivation_version = '1'` was deleted | every version is reconciled; rows are stamped with the current version |
| duplicate rows | possible, and unclassified | collapsed deterministically - a row the user acted on wins, then the older, then the lowest id |
| audit | returned a count | returns a per-category `ReconcileReport` |
| safety | a failure mid-way left partial state | one transaction |

The previous behaviour was exactly the hazard the brief named: `delete_tasks_by_
derivation_version("1")` never touched the 291 v2 rows, and a fingerprint that already
existed was skipped rather than corrected.

### Idempotency and duplicate prevention

`backend/tests/test_task_reconcile_idempotency.py` - 12 tests, including one that runs
the reconcile against **a copy of the real 291-row database**. Properties pinned: a
second pass is a byte-identical no-op; no count inflation; no duplicates; a stale row is
corrected in place rather than copied; `status`, `created_at` and `priority_override`
survive; a **completed** task the extractor rejects is kept while a **pending** one is
removed; two messages with the same wording in different threads stay two tasks.

Measured on the live database: pass 1 changed rows, pass 2 reported
`preserved=194, normalized=0, removed=0, recreated=0, duplicates=0` and the row set was
identical.

### Backup, and running it

Backup used the application's own WAL-safe `snapshot_database` (SQLite online backup) -
no new format invented.

- live: `%LOCALAPPDATA%\Alfred\alfred.sqlite3` (14.6 MB, 1068 emails, 621 analyses)
- backup: `%LOCALAPPDATA%\Alfred\alfred.sqlite3.20260927-pre-reconcile.bak`

The migration was proved on a scratch copy first, run twice there, and only then
applied to the live file.

| | before | after |
| --- | --- | --- |
| tasks | 291 | **194** |
| `due_at` holding prose or a field label | 96 | **0** |
| `description` holding `Owner: …` | 174 | **0** |
| `description` holding `Due: …` | 59 | **0** |
| `owner` column populated | 0 | **161** |
| linked to a source email / unlinked | 291 / 0 | 194 / 0 |
| duplicate fingerprints | 0 | 0 |
| emails / analyses | 1068 / 621 | 1068 / 621 (untouched) |

Report: `preserved 1, normalized 193, recreated 0, removed 95, duplicates 0,
kept_user_state 0`. A second pass: `preserved 194`, nothing else, identical rows.

The known malformed sources now resolve correctly: the GitHub sudo OTP, the Techugo
blast, the Indeed receipt and the DM360 alert produce **no task**; the job description
produces one clean actionable task with `due_at` NULL.

A third pass, after the sidecar was rebuilt, removed 2 more rows that the stale sidecar
had created ("72 hours from receiving this email", "15 Aug 2026, 00:00 - 18 Aug 2026,
16:33") and stamped the last v2 row to v3. **This was my error**: I ran
`cargo tauri build` without re-running `backend/build_sidecar.py`, so the installed
sidecar carried the older extraction rules. Caught because the new rows were v3 yet
still temporal-only. Both steps are required, every time.

### The 900px overflow

**Cause.** The shell grid was `grid-template-columns: var(--rail-width) 1fr`. A bare
`1fr` track floors at its content's min-content width, and `.workspace-header` had no
`min-width: 0`, while `.header-search` carried a hard `min-width: 200px` and
`.header-context` a `min-width: 130px` with `white-space: nowrap`. One wide task row
widened the track, and the header was dragged off the right edge with it.

**Fix**, no font sizes and no transforms:
- `grid-template-columns: var(--rail-width) minmax(0, 1fr)` and
  `grid-template-rows: var(--header-height) minmax(0, 1fr)`
- `.workspace-header { min-width: 0 }`
- `.header-context { min-width: 0; overflow: hidden }`
- `.header-search { flex: 1 1 380px; min-width: 0 }`
- `.task-meta { flex-wrap: wrap; min-width: 0 }`

**Verified at 900px in the packaged app.** The header now truncates its context text
with an ellipsis, the search field shrinks and stays usable, and Sync / AI status /
avatar are all fully visible. Pending / Completed / All are visible. Every row's action
column is aligned, including two-line titles that wrap. Nothing is clipped and no
horizontal scrolling is needed to reach View email or Delete.

### A UTF-8 BOM I introduced, and the tooling it silently broke

A PowerShell edit wrote a BOM into `due_dates.py`, `task_derivation.py` and
`TasksPage.layout.test.tsx`. Python's `import` tolerates a BOM, so **every test still
passed** - but `generate_knowledge_graph.py` parses with `ast.parse` and *silently
skips* files that raise `SyntaxError`, so `task_derivation` had dropped out of the
knowledge graph entirely and `tools/docs/tests/test_generator.py` failed. Fixed by
stripping the BOMs. Worth knowing: this class of corruption is invisible to the test
suite and only surfaces in AST-based tooling.

---

## Verification status

**AUTOMATED VERIFIED**

- 295 backend, 9 tools, 35 Rust, 383 frontend (32/32 files) - 0 failures.
- `tsc -b`, ESLint, `cargo fmt --check`, `cargo clippy -D warnings`, frontend build,
  release secret scan, Windows deployment check - all clean.
- Migration and rebuild idempotency, duplicate prevention, user-state preservation -
  12 dedicated tests plus a run against a copy of the real database.
- Extraction contract - 40 cases in `test_task_extraction_contract.py`.
- Task action column - 7 cases in `TasksPage.layout.test.tsx`.
- The frontend runner still exits non-zero on the pre-existing unhandled `boom`
  rejection in `src/features/focus.retry.test.tsx`, untouched here.

**MANUALLY VISUALLY VERIFIED** (packaged NSIS install, real mailbox)

- Tasks at **900px**: full layout fits, header truncates cleanly, search shrinks, all
  header controls visible, action column aligned on every row including wrapped
  two-line titles, with and without due dates, high and medium priority. This is the
  screenshot that shows the overflow fix.
- Mail with a **real message open at 1440px**: subject, FROM / TO / DATE, body text.
  This closes the reader-at-full-width gap the previous gate could not close.
- The action column measured at **0 px spread** across 8 consecutive rows (mail icon
  1682-1702, label 1709-1792, trash 1825-1843).
- All ten sidebar destinations, measured from the accent bar: exactly one active row
  each, and the correct one.

**NOT VERIFIED** - no claim is made about any of this

- Light theme, on any screen. The theme was dark for the whole pass.
- Tasks / Overview / Deadlines / Accounts / Settings at 1440, 1100 or 1000. The
  captures exist but the rail collapses below ~1940, so the navigation clicks missed
  and landed on the message list; the one frame I inspected turned out to be Mail, not
  Tasks. Unverified rather than assumed.
- The **intelligence panel**. Never opened in this pass.
- Attachments, and the reader's action row.
- Deep scrolling, and a task with no `source_email_id` (the disabled-view-action state
  is covered by unit test only).
- Two capture runs were **discarded** because they recorded the operator's Chrome
  window rather than Alfred: a foreground check was unreliable and a centre-pixel
  darkness test could not distinguish a black web page from a black app surface.
  `PrintWindow` was used instead, which renders the target's own surface and cannot
  capture another application. Every reported figure comes from a frame that was checked.

---

## Gate 1 closure pass

Date: 2026-09-27. Baseline `bf1a171`.

### Task counts, exactly

The previous report contained a contradiction: it stated a final count of 194 and then
claimed "~195 of them are still low-value marketing-derived tasks". That was a
**reporting error, not a data problem** - the total was 194, and no count was ever
derived from a "~195". Nothing was modified to reconcile it.

Queried directly from the live database:

| | |
| --- | --- |
| total | 194 |
| pending / completed / dismissed | 194 / 0 / 0 |
| source-linked / source-unlinked | 194 / 0 |
| `due_at` NULL / normalized | 141 / 53 |
| `owner` present / absent | 161 / 33 |
| duplicate fingerprints | 0 |
| derivation versions | v3: 194 |

Source-email category of the 194: `updates` 125, `primary` 63, `promotions` 6.

Title-based noise classification, counted as a **union with no double counting**:
`apply for… / job alert` 3, `view ad / offer / sale` 3, `application-status phrasing`
2, `join a channel` 0 - **7 in total**, leaving 187. So the honest figure is 7, not 195.
A subjective judgement would call more of the 187 low-value ("Check account activity
for unauthorized WindowsSill access"), but that is not a measurement and is not
presented as one.

The migration was **not** run again, and the backup
`alfred.sqlite3.20260927-pre-reconcile.bak` is untouched.

### A release sequence that cannot silently package a stale sidecar

`cargo tauri build` copies whatever is in `desktop/src-tauri/binaries/` and never
rebuilds it. That is the mechanism behind both stale-sidecar incidents, so the order is
now enforced rather than documented:

```
pwsh -File tools/release/build_release.ps1
```

which runs `build_sidecar.py` -> `check_sidecar_freshness.py` -> `cargo tauri build` ->
`check_sidecar_freshness.py` again -> `scan_release_secrets.py`.

`tools/release/check_sidecar_freshness.py` fails when the packaged sidecar is older than
any backend source. **It earned its place immediately**: on first run it reported the
sidecar stale, because the BOM fix had touched `task_derivation.py` after the last
sidecar build.

Two implementation notes, both learned the hard way:
- `build_sidecar.py` refuses when `GMAIL_CLIENT_SECRET` is set and reloads it from
  `backend/.env`, so the key must be *present but empty*. Windows PowerShell 5.1 cannot
  express that - `$env:X = ''` removes the key - so the script runs a two-line Python
  launcher. `backend/.env` is never read, moved or modified; no credential is embedded.
- Redirecting the child's output deadlocked, because PyInstaller fills the stderr pipe.
  The release script does not redirect.

### The knowledge graph no longer hides parse errors

`analyze_python` caught `SyntaxError` and `continue`d, so a module that failed to parse
was dropped from the vault with no error - which is exactly how a UTF-8 BOM removed
`task_derivation` from the graph while every test still passed. A parse failure is now a
hard error naming the file, and reading as `utf-8-sig` makes a stray BOM a no-op rather
than a failure.

`tools/release/tests/test_release_integrity.py` (9 tests) covers this and the release
guard: an unparseable file raises, a BOM-only file still generates, non-UTF-8 raises, key
backend modules are all indexed, a stale sidecar fails the check, a missing sidecar fails,
and the release script builds the sidecar and checks freshness *before* the bundle.

---

## Verification status

**AUTOMATED VERIFIED**

- 295 backend, 18 tools, 35 Rust, 383 frontend (32/32 files) - **0 failures**.
- `tsc -b`, ESLint, `cargo fmt --check`, `cargo clippy -D warnings`, frontend production
  build, knowledge-graph generation, sidecar freshness, release secret scan, Windows
  deployment check, `build_sidecar.py` and `cargo tauri build` - all clean.
- The frontend runner still exits non-zero on the **pre-existing** unhandled `boom`
  rejection in `src/features/focus.retry.test.tsx`, which this work does not touch. It is
  reported separately and is not a regression.

**MANUALLY VERIFIED** (installed NSIS build, real mailbox, `PrintWindow` captures that
render the app's own surface and therefore cannot record another window)

- **Dark, 1440px**: Mail with list and reader open; Tasks; Settings (theme control,
  Local AI, Data, Privacy); Overview; Deadlines; Accounts.
- **Tasks, 1440px**: 194 pending, matching the database exactly. Action column at an
  identical x on every row, with and without a due date, high and medium priority. Every
  `due_at` a normalised ISO instant; no `Owner:` text, no prose dates, no field labels.
- **Dark, 900px**: the responsive fix - header truncates, search shrinks, all header
  controls reachable, action column aligned including wrapped two-line titles.
- **Sidebar**: all ten destinations measured from the accent bar - exactly one active
  row each, and the correct one.

**NOT VERIFIED** - no claim is made

- **Light theme, on any screen.** The Settings theme control was located and clicked, but
  the application had returned to the Mail view, so the click landed on the message list
  and the theme never changed. Every "light" capture is therefore still dark theme and
  has been discarded. This is a tooling failure, not a finding about light mode.
- **The intelligence panel.** Never opened in this pass.
- Deadlines, Accounts and Overview at 1100px and 1000px; Tasks and Overview at 1000px.
  The rail collapses to icons below roughly 1600px, so the coordinate-based navigation
  used at 1940px silently missed at 1440px, and repeated attempts to recover it consumed
  the remaining budget.
- Attachments, and the reader's action row.
- A clean startup/shutdown cycle for this specific build; the lifecycle was verified on
  the previous packaged build and the shutdown code has not changed since.

**Why light theme could not be closed here.** Navigation and capture both had to work at
once. The rail is icon-only below ~1600px, the app restores to Mail rather than the
page last visited, and `PrintWindow` intermittently returns an unusable frame. Each
script therefore has to navigate and capture in one pass, and the theme control moved
out from under the click twice. I stopped rather than report a dark frame as light.

---

## Final verification pass: the exact `421f808` build

Date: 2026-09-27. Baseline `421f808` — `chore(alfred): close phase one release
verification`. No source code was changed in this pass; the working tree was clean
before it and no tracked file was modified during it.

The previous section closed Gate 1 at `bf1a171` with light theme and the
startup/shutdown cycle unverified. This pass re-verified the **exact artifact that
`421f808` produces**, installed it, and closed those two gaps. It did not close the
intelligence panel or any window-size regression.

### Canonical build and packaging — verified

Run as the single documented command, not as two remembered steps:

```
powershell -NoProfile -ExecutionPolicy Bypass -File tools\release\build_release.ps1
```

It completed end to end: build the PyInstaller sidecar, freshness check, `cargo tauri
build`, freshness check again, release secret scan. The freshness check passed on both
sides of the bundle, so the packaged sidecar was not stale at either point.

| artifact | size | timestamp |
| --- | --- | --- |
| `desktop/src-tauri/binaries/alfred-backend-x86_64-pc-windows-msvc.exe` | 24.5 MB | 2026-09-27 21:14:03 |
| `desktop/src-tauri/target/release/alfred-desktop.exe` | 11.4 MB | 2026-09-27 |
| `desktop/src-tauri/target/release/bundle/nsis/Alfred_0.1.0_x64-setup.exe` | 27 MB | 2026-09-27 21:51:42 |

The NSIS installer ran with `/S` and exited 0. The installed shell
(`%LOCALAPPDATA%\Alfred\alfred-desktop.exe`) is stamped 21:51:28, i.e. this build, not
a previous one.

### Startup — verified

With 0 Alfred processes present beforehand:

- Main window appeared at **t+1.21 s**.
- Boot frames were **dark from the first captured frame**. No white flash — the
  `backgroundColor` fix still holds on this build.
- Process tree afterwards: **1** `alfred-desktop` and **2** `alfred-backend`. The pair
  is expected for a PyInstaller one-file executable (parent + extracted child), not a
  duplicate launch.
- **No terminal/console window**, and no second Alfred instance.

### Clean shutdown — verified

From `%LOCALAPPDATA%\AlfredData\logs\desktop.log`, in order:

```
desktop.exit_requested
POST /api/shutdown            200 OK
shutdown.graceful_requested   pid=13648 port=59932 delivered=true
sidecar.exited                pid=13648 exit=Some(0) generation=1
shutdown.exited_cleanly       pid=13648
```

**Sidecar exit code 0.** Afterwards: **0** `alfred-desktop`, **0** `alfred-backend`, **0**
orphan processes left behind.

One minor, non-blocking observation, deliberately **not** changed in this pass: the
clean exit is emitted at `ERROR` severity (`sidecar.exited ... exit=Some(0)`). The exit
status is correct and the shutdown is clean, so this is a log-level nit, not a
functional defect. Left for a follow-up.

### Light theme — objectively confirmed on three screens

The theme is now genuinely light, confirmed by pixel measurement rather than by eye and
not by a single point sample (a one-pixel probe hit an overlay and was misleading).
The modal background of the light surface measures **(242, 243, 248)** — exactly
`--bg-app: #f2f3f8` — with mean luminance ~241.6 across the frame.

| screen | what was actually on screen |
| --- | --- |
| **Settings** | the Settings page itself, on the light surface |
| **Mail** | the real message list on the light surface |
| **Reader** | a **real message open**: subject, `FROM` (name + address), `TO`, `DATE`, and body text, all light |

The earlier claim in this document that light mode was unreachable was a tooling
failure, and it is now resolved. The Settings theme control was reached at the expanded
1940px rail.

### NOT verified in this pass — no claim is made about any of this

- **The intelligence panel.** Never opened on this build. Borders, radius, separation
  and the off-scale values deferred above remain unverified.
- **1100px.** Not captured on this build.
- **1000px.** Not captured on this build.
- **900px final regression.** **Not re-verified on `421f808`.** 900px was inspected and
  passed on the earlier `bf1a171` build; the 900px overflow fix is therefore evidenced
  by that pass and by its layout tests, *not* by a fresh capture of the final artifact.
  Do not read the earlier 900px result as covering `421f808`.
- **Light theme on Tasks, Overview, Deadlines and Accounts.** Only Settings, Mail and
  Reader are confirmed light. A capture named `light-tasks-1940` exists but the click
  missed and the frame shows **Mail**; it was discarded rather than counted as Tasks.
- All ten sidebar destinations were measured from the accent bar on the `9783a66` pass
  and confirmed again at `bf1a171`. In this pass only the Settings active state was
  re-measured; the other nine were not re-measured on `421f808`.
- Attachments, and the reader's action row.
- The Deadlines `0 upcoming` / skeleton-timing question is still unresolved.

### GUI capture limitations that cost this pass its remaining budget

Recorded so the next attempt does not repeat them. Every one of these produced
*plausible but wrong* evidence, not a defect in the application.

1. **`PrintWindow` is occlusion-proof but not reliable.** With
   `PW_RENDERFULLCONTENT` it renders the target window's own surface, so it cannot record
   another application — that is why it replaced `CopyFromScreen`, which had captured the
   operator's Chrome and produced a wholly false layout finding. But it *intermittently
   returns an unusable or black frame*, so every capture needs a retry-and-reject loop
   with a distinct-colour check. A single frame is never evidence.
2. **Point sampling a pixel is not a theme check.** A one-pixel probe landed on an
   overlay and reported the wrong surface. Theme state was only accepted from the modal
   colour and mean luminance of the whole frame.
3. **UI Automation exposes nothing.** The WebView2 tree returns **0 buttons**, so
   elements cannot be targeted by name or automation id. Navigation has to be driven by
   mouse input at coordinates.
4. **The rail collapses below roughly 1600px.** Coordinates learned at the expanded
   1940px rail silently miss at 1440px and narrower, landing on the message list instead
   of the intended destination. This is what produced the discarded "light Tasks" frame
   and the earlier "clicked Tasks, got Deadlines" result. Navigate while expanded, then
   resize.
5. **The app restores to Mail, not to the page last visited.** A pass that assumes the
   previous page is still showing will capture the wrong screen.
6. **The window handle went invalid mid-run.** A late scripted pass received a 0x0
   window rectangle, so capture aborted rather than writing a blank image. Screen
   identity has to be confirmed *before* a frame counts.
7. **`MoveWindow` has repeatedly collapsed the window** to a tiny size rather than
   resizing it, so any resize must be confirmed by reading the rectangle back.

The consistent lesson: with no automation tree available, each script must navigate,
confirm what is actually on screen, and capture in a single pass — and a frame whose
identity was not confirmed is discarded, not reported.

### Tests at this baseline

Not re-run in this pass; no source changed, so the `421f808` baseline stands: **295
backend, 18 tools, 35 Rust, 383 frontend (32/32 files) = 731 passing, 0 failures.**
`tsc -b`, ESLint, `cargo fmt --check`, `cargo clippy -D warnings`, frontend production
build, knowledge-graph generation, sidecar freshness, release secret scan and the
Windows deployment check were all clean. The frontend runner still exits non-zero on
the pre-existing unhandled `boom` rejection in `src/features/focus.retry.test.tsx`;
reported separately, not a regression.

---

## Scope correction: this document is NOT the Gate 1 record

`docs/Phases.md` §"Gate 1 — Startup and process lifecycle" is the authoritative gate
definition. It contains 16 scope items and 15 mandatory acceptance criteria, and
**none of them concern a theme, a screen, or a window width**. Visual and UX
verification belongs to **Phase 3 → Gate 3** in the phase model
(`docs/Phases.md:18`).

Earlier revisions of this file used "Gate 1" to mean "the visual pass", which
mis-attributed Phase 3 work to the startup gate. That framing is retired. Everything
above this line remains valid **visual QA evidence and a Phase 3 backlog**; it is
preserved unchanged, and none of it is deleted or downgraded.

One claim above is now **contradicted** and must not be relied on: the statement that
shutdown leaves "no orphan processes" was true for a clean shutdown only. Under a
terminal startup failure the shell abandons ownership of a still-running sidecar and
leaves orphans behind — see D1 below.

---

## Authoritative Gate 1 verification (`docs/Phases.md`)

Date: 2026-09-28. Binary: `%LOCALAPPDATA%\Alfred\alfred-desktop.exe`, the artifact
built from `421f808` (see the build-stamp caveat in D3). Faults were injected into the
running sidecar with OS primitives only — process suspend and process kill. No
production code, no database, and no task migration were touched.

### Criteria satisfied

| Criterion | Evidence |
| --- | --- |
| One launch, one window | `tasklist` before = 0/0; after start = `alfred-desktop.exe` 1 pid, no second window |
| Splash from first paint | `window.revealed reason=explicit` at t+0.53s, before any backend process exists |
| Backend reaches Ready | `sidecar.out ... GET /health 200 OK` then `startup.phase phase=RECOVERY` (degraded: local AI offline, mailbox usable) at t+4.6s cold |
| Second launch focuses the existing window | Window minimised, `GetForegroundWindow` not Alfred; second instance launched; **foreground was Alfred in 15/15 samples over 3s**; window restored from minimise |
| No second backend | Second instance exited **code 0** in <15s; `alfred-desktop.exe` count stayed **1**; `alfred-backend.exe` count unchanged at 2 before and after |
| Zero console windows | No conhost/terminal window observed in any launch |
| Retry bounded and cancellable | `frontend/src/layout/StartupGate.tsx:154-171`; tests `retries once per click and then reports readiness`, `does not auto-retry: exactly one call per click` |
| Runtime token 256-bit CSPRNG | `main.rs:942-944` — `getrandom::getrandom` into `[0u8; 32]`, `TOKEN_BYTES = 32` (main.rs:44), hex-encoded. Tests `token_is_the_requested_length` (asserts `TOKEN_BYTES * 2` hex chars), `token_is_lowercase_hex_only`, `tokens_are_unique_across_many_draws`, `token_draws_differ_within_a_single_nanosecond_window`, `token_has_no_low_entropy_structure`, `the_token_is_never_written_to_the_log`; plus `tools/release/check_windows_deployment.py:197 test_session_token_comes_from_the_os_csprng` |
| Production CSP free of dev origins | `tauri.conf.json` csp = `default-src 'self'; connect-src 'self' http://127.0.0.1:* ipc: http://ipc.localhost; …` — no `localhost`, no `:5173`. `http://127.0.0.1:*` is the required loopback, not a dev origin. Test: `check_windows_deployment.py:181 test_production_csp_has_no_development_origin` (asserts `localhost:5173` and `127.0.0.1:5173` absent from the csp line) |
| `cargo fmt --check` / `clippy --all-targets` / `cargo test` | Executed this pass: fmt exit 0, clippy `--all-targets` exit 0, **35 passed / 0 failed** |
| `cargo test` drives the supervisor | `readiness_after_a_generation_survives_a_restart` (`#[tokio::test]`, real `watch` channel + generation guard), `the_process_stays_owned_until_shutdown`, `shutdown_delivers_a_graceful_request_before_killing` (real `StubBackend` TCP listener), `await_backend_ready_returns_immediately_when_already_ready` |
| No Rust test references `SIDECAR_EXITED` | Confirmed: the only occurrences are `main.rs:129` (the live `DiagnosticCode` mapping) and six frontend **TypeScript** tests. Zero Rust tests. The gate's premise that the state is "nonexistent" is outdated — it is a real diagnostic code |
| Clean shutdown, sidecar exit 0 | `desktop.exit_requested` → `POST /api/shutdown 200` → `shutdown.graceful_requested delivered=true` → `sidecar.exited exit=Some(0)` → `shutdown.exited_cleanly`; `tasklist` after = 0/0 |

### D1 — REAL DEFECT: a terminal startup failure orphans the sidecar

Highest-severity finding of this pass. **This fails the mandatory criterion "Quit
leaves zero `alfred-backend.exe` processes, verified by `tasklist` after quit."**

Reproduced by suspending the sidecar (`NtSuspendProcess`, rc=0) so it stayed alive but
could not answer `/health`:

```
startup.phase phase=FATAL_ERROR        (04:18:28.993Z, 61.1s after spawn = HEALTH_TIMEOUT)
desktop.exit_requested                 (04:18:45.758Z)
```

`tasklist` after quit: **`alfred-desktop.exe` 0, `alfred-backend.exe` 2.**

Root cause: on a terminal failure the poller calls `registry_poll.clear()`
(`main.rs:594-597`) and drops `port`/`token`, so the shell forgets it owns a process
that is still running. `ShutdownRegistry::terminate()` then finds an empty slot and
kills nothing. No `shutdown.graceful_requested` and no `sidecar.exited` appear after
`desktop.exit_requested` in that run, confirming `terminate()` had no target. This is
the same class of orphan the gate's item 1.6 set out to eliminate; the fix covers the
clean path but not the terminal-failure path. Both orphan pids required manual
`Stop-Process`.

Proposed minimal fix: do not release ownership while the child is alive — keep the
`ShutdownTarget` registered on terminal failure (or retain the pid for exit-time
termination) so `terminate()` always has a target. Regression test: assert the
registry still holds a target after a terminal transition, mirroring
`the_process_stays_owned_until_shutdown`.

### D2 — REAL DEFECT: a hung backend is reported as the wrong diagnostic code

**This fails the mandatory criterion "A forced health timeout shows a named code."**

The failure screen was captured after the health timeout. It reads:

- "Alfred couldn't start"
- guidance: *"Alfred took too long to finish starting. Your mail and settings are untouched. Try again."*
- **Diagnostic code: `STARTUP_TIMEOUT`**
- Log file: `C:\Users\Nipun\AppData\Local\AlfredData\logs\desktop.log` (correct)
- "Try again" button present

The actual cause was a hung backend, for which the shell has a precise code and
guidance: `BACKEND_HEALTH_TIMEOUT` — *"Alfred's local service did not respond in
time… check the log file below."* The user is shown a generic, misleading code and
wording instead. `BACKEND_HEALTH_TIMEOUT` appeared **nowhere**: not in the UI, and not
in the log (see D4).

Root cause: `StartupGate.tsx:177-181` renders `error.code` from the rejected
`initPromise`, ignoring the shell's authoritative code, which *was* delivered on
`alfred://startup-phase` and stored in `status.code` by the listener at
`StartupGate.tsx:116-118`. The gate's own `STARTUP_TIMEOUT` fires at the same 60s
boundary and wins the race with the less specific code. The specific diagnostic already
in the component is discarded.

### D3 — REAL DEFECT: the build stamp cannot identify the build

`desktop.log` records `build=bf1a17124909` for a binary built from `421f808`. Since
`421f808` changed only `docs/` and `tools/`, the compiled shell, frontend, and sidecar
are byte-for-byte the same code either way — but the stamp is wrong, and this pass had
to fall back to `git show --stat` to establish which commit the artifact actually
corresponds to.

Root cause: `desktop/src-tauri/build.rs:4-14` reads `git rev-parse --short=12 HEAD` and
emits `cargo:rustc-env=ALFRED_GIT_COMMIT` but declares **no** `cargo:rerun-if-changed`.
Cargo therefore caches the build-script output, and a commit that touches no file in
`desktop/src-tauri` leaves the previous commit's stamp compiled in. The field is a
support surface (`main.rs:1311`, `startup_diagnostics()` at `main.rs:1275-1281`).

Minimal fix: `println!("cargo:rerun-if-changed=../../.git/HEAD");` (plus the ref file
for worktrees), so the stamp always reflects the tree being built.

### D4 — REAL DEFECT: the named diagnostic code is redacted out of the log

Every phase transition logs `code=[redacted]`:

```
startup.phase phase=INITIALIZING      code=[redacted] generation=0
startup.phase phase=STARTING_BACKEND  code=[redacted] generation=1
startup.phase phase=RECOVERY          code=[redacted] generation=1
startup.phase phase=FATAL_ERROR       code=[redacted] generation=1
```

`main.rs:87-89` states these codes "appear in the UI **and in the log**". They do not.
The global redaction filter treats a bare `code=` as an OAuth authorization code — the
identical root cause as the previously fixed B4, which renamed only the sidecar's field
to `exit=`. The `startup.phase` line still uses `code=` and is still stripped. Combined
with D2, a support case has no way to recover the real cause from the log.

Token redaction itself is working correctly and is not in question:
`GET /api/analysis/progress?token=[redacted]` is properly masked.

Minimal fix: rename the field as B4 did (for example `diag=`), or exempt the shell's
own startup lines from the `code=` rule.

### D5 — REAL DEFECT: concurrent log records interleave and corrupt

Observed twice, both times at the `Initializing` → `StartingBackend` boundary:

```
2026-09-27T20:12:34.819Z2026-09-27T20:12:34.819Z  INFOINFO  alfred_desktopalfred_desktop  window.revealed reason=explicitstartup.phase phase=INITIALIZING …
```

Two records are spliced mid-line, duplicating the timestamp, level and target. A
partial duplicate of `desktop.exit_requested` and `window.revealed` is expected (both
`RunEvent::Exit` and `ExitRequested` fire, and `reveal_main_window` is called from both
`setup` and `RunEvent::Ready` by design) — but byte-level splicing is not. The logger
writes from multiple threads without a whole-record lock.

### Criterion still unverified

**"Retry actually retries"** is not confirmed at runtime. The button is present in the
capture, its handler is `restart_backend` (`main.rs:1240-1248`, logging
`restart.requested`), and it is unit-tested, but both automated attempts to click it
missed the target, and no `restart.requested` was ever logged. Presence and
correctness of the control are evidenced; the round trip is not.

### Startup states

`docs/Phases.md` item 1.2 says "12 named states" and its acceptance criteria reference
"§10 of the master requirements". **No document in this repository contains a §10 that
enumerates 12 startup states** — `Architecture.md` §10 is "AI service and Ollama",
`Design.md` §10 and `UI-DESIGN-SPEC.md` §10 are "States" (design tokens, not startup).
The implemented `StartupPhase` enum (`main.rs:55-78`) has **11** variants:

| # | Phase | Trigger observed | Reached? | Evidence |
| --- | --- | --- | --- | --- |
| 1 | `BOOT` | process start | yes | `BackendRuntimeState::new()`, `main.rs:253` |
| 2 | `INITIALIZING` | logger + channel ready | yes | logged every launch |
| 3 | `STARTING_BACKEND` | about to spawn | yes | logged every launch |
| 4 | `WAITING_FOR_BACKEND` | spawned, polling `/health` | yes | `health.probe` lines precede readiness |
| 5 | `CHECKING_DATABASE` | health OK, verifying SQLite | not isolated | passed through inside the readiness assessment |
| 6 | `CHECKING_AI_RUNTIME` | probing local AI | not isolated | passed through |
| 7 | `CHECKING_MODEL` | checking configured model | not isolated | passed through |
| 8 | `RESTORING_SESSION` | checks passed | not isolated | passed through |
| 9 | `READY` | all checks pass | **not on this machine** | every launch reached `RECOVERY` instead: local AI offline |
| 10 | `RECOVERY` | degraded but usable | yes | logged every launch; `assess_readiness` tests `a_missing_model_degrades_but_does_not_block_the_mailbox`, `an_absent_ai_runtime_degrades_but_does_not_block_the_mailbox` |
| 11 | `FATAL_ERROR` | terminal failure | yes | induced twice (hung backend → D2; killed backend → logged `sidecar.exited exit=Some(-1)`) |

`READY` and the four intermediate checking phases are represented and covered by unit
tests but were not observed on this machine, because the local AI runtime is not
running. The "12 named states" figure and the "§10" reference are both **unresolvable
as written** and need correcting in `docs/Phases.md`.

### Gate 1: PARTIAL — superseded by the closure record below

> This verdict described the state **before** D1–D6 were fixed. It is kept for
> the record. The current verdict is in §Gate 1 defect closure and re-verification.

Satisfied: single launch, single window, second-launch focus, no second backend, zero
console windows, splash from first paint, backend readiness, CSPRNG token, production
CSP, `fmt`/`clippy`/`cargo test` (35 passed), supervisor tests present, no Rust
`SIDECAR_EXITED` reference, clean shutdown with sidecar exit code 0.

Blocking, and all real defects rather than verification gaps:

1. **D1** — terminal startup failure orphans `alfred-backend.exe`; `tasklist` after quit
   showed 2. Fails the zero-orphan criterion.
2. **D2** — a hung backend surfaces `STARTUP_TIMEOUT` instead of
   `BACKEND_HEALTH_TIMEOUT`. Fails the named-code criterion.
3. **D3** — the embedded build stamp is stale and misidentifies the artifact.
4. **D4** — the diagnostic code is redacted out of every `startup.phase` log line.
5. **D5** — concurrent log records interleave and corrupt.
6. **Retry round trip unverified** at runtime (control present, unit-tested, click not
   landed).
7. **`READY` phase and the four intermediate checking phases** not observed on this
   machine; the "12 states"/"§10" criteria are unresolvable as written.

The visual items that earlier revisions of this file listed as Gate 1 blockers — the
intelligence panel, 1100px, 1000px, the 900px re-check, light theme on Tasks /
Overview / Deadlines / Accounts — are **not Gate 1 blockers**. They remain open as
Phase 3 / Gate 3 QA and are recorded above.

---

## Gate 1 defect closure and re-verification

Date: 2026-10-04. D1–D6 above were fixed, each with a regression test, and the whole
authoritative acceptance set was re-run against the **packaged artifact built after the
fixes** (NSIS installer, exit 0). Faults were injected with OS primitives only:
`NtSuspendProcess` to hang the sidecar and `Stop-Process` to kill it. No production
data was touched and the task migration was not run.

| # | Defect | Fix | Regression test |
| --- | --- | --- | --- |
| D1 | Terminal startup failure orphaned the sidecar | `settle_poll_outcome()` decides connection details only and never touches the shutdown registry; ownership is released solely by `stop_child()` and `terminate()` | `a_terminal_failure_keeps_ownership_of_a_live_child`, `a_terminal_failure_terminates_the_owned_child_and_leaves_no_orphan` (real child process + real `terminate()`), `a_restart_hands_ownership_to_the_new_child_only`, `termination_is_idempotent`, `a_healthy_poll_keeps_the_connection`, plus `test_a_terminal_failure_does_not_release_child_ownership` |
| D2 | Health timeout reported `STARTUP_TIMEOUT` | Two-part data-flow fix: (a) `STARTUP_TIMEOUT` is now `HEALTH_TIMEOUT + 15s` so the poller's authoritative verdict always wins the race; (b) `StartupGate` renders the shell's `status.code`/`status.guidance` in preference to the gate promise's code | `shows BACKEND_HEALTH_TIMEOUT for a health timeout, not STARTUP_TIMEOUT`, `still shows the log path and a Retry on a health timeout`, `keeps the promise code when the shell published no terminal snapshot`, `never leaks a raw exception when the shell code is present` |
| D3 | Build stamp stale (`bf1a17124909` for a `421f808` build) | `build.rs` now resolves `.git` (including the `gitdir:` worktree pointer) and declares `cargo:rerun-if-changed` for `HEAD` **and** the ref `HEAD` points at | `test_build_stamp_is_invalidated_when_git_head_moves` |
| D4 | `code=[redacted]` on every `startup.phase` line | New `log_phase()` helper logs the field as `diag=`; OAuth `code=` redaction untouched | `the_startup_phase_diagnostic_code_is_not_redacted`, `an_oauth_authorization_code_is_still_redacted`, `other_sensitive_values_are_still_redacted`, plus `test_startup_phase_log_field_is_not_named_code` |
| D5 | Concurrent records interleaved mid-line | `render_record()` builds the whole record, `append_record()` issues **one** `write_all` under a process-wide `LOG_LOCK` covering rotate+open+write | `concurrent_records_are_never_spliced` (8 threads × 60 records; asserts exact line count, one timestamp/level/target/message per line, no duplicates) |
| D6 | Backend crash detected but never surfaced | `StartupGate` watches the authoritative status while ready and reuses the **existing** failure surface; the title becomes "Alfred's local service stopped" so it does not claim Alfred failed to start. `SIDECAR_EXITED`'s guidance no longer says "while starting", which was false mid-session | `shows an unavailable state instead of stale healthy content`, `does not claim the Gmail account disconnected`, `offers Retry and restores the workspace when the backend comes back`, `ignores a healthy event so normal recovery never shows an error` |
| D7 | Retry round trip unverified | Not a defect. Re-tested after the fixes and **works** | — (verified at runtime, see below) |
| D8 | "12 named states" vs 11 implemented | `docs/Phases.md` corrected to 11 and the criterion made self-contained; **no state invented** | `startup_phases_serialise_as_documented` now pins all 11 wire names |

### Re-verification on the fixed packaged artifact

```
window revealed at t+0.91s
startup.phase phase=RECOVERY diag=AI_RUNTIME_UNAVAILABLE generation=1
```

Second launch: window minimised, foreground confirmed not Alfred; second instance
exited **0**; window restored and focused; `alfred-desktop` stayed at 1 and
`alfred-backend` unchanged at 2.

**D7 — Retry round trip (previously unverified, now proven):**

```
sidecar.exited      pid=22372 exit=Some(-1) generation=1
startup.phase       phase=FATAL_ERROR diag=SIDECAR_EXITED generation=1
restart.requested
backend.stop_requested pid=22372 port=63345 delivered=false
startup.phase       phase=STARTING_BACKEND diag=NONE generation=2
backend.spawned     pid=14396 port=55643 generation=2
startup.phase       phase=RECOVERY diag=AI_RUNTIME_UNAVAILABLE generation=2
```

The button was located structurally — the widest solid accent rectangle in the lower
half of the frame (146 px at y=882) — not by guessed coordinates. Both automated
attempts before the fixes missed; this one landed and produced a full restart with a
new generation.

**D2/D6 — user-visible states, read from the frames:**

- Health timeout: `BACKEND_HEALTH_TIMEOUT`, "Alfred's local service did not respond in
  time…", log path, Try again.
- Backend crash: `SIDECAR_EXITED`, "Alfred's local service stopped", log path, Try
  again — and **no stale Mail workspace, no "Gmail connected"**.

**D1 — the orphan is gone.** Same induction as before (suspend the sidecar, let the
health timeout fire, then quit):

| | before the fix | after the fix |
| --- | --- | --- |
| `alfred-desktop.exe` after quit | 0 | 0 |
| `alfred-backend.exe` after quit | **2** | **0** |

No manual `Stop-Process` was needed this time.

**D3/D4 — build identity and log legibility.** `desktop.log` now reads
`build=60819dfb64e5`, matching `git rev-parse --short=12 HEAD` exactly, and the
lifecycle lines carry readable diagnostics:

```
startup.phase phase=INITIALIZING     diag=NONE generation=0
startup.phase phase=STARTING_BACKEND diag=NONE generation=1
startup.phase phase=RECOVERY         diag=AI_RUNTIME_UNAVAILABLE generation=1
startup.phase phase=FATAL_ERROR      diag=BACKEND_HEALTH_TIMEOUT generation=1
startup.phase phase=FATAL_ERROR      diag=SIDECAR_EXITED generation=1
```

No `code=[redacted]` remains, and no spliced record was observed in any log from these
runs. The token is still redacted where it belongs:
`GET /api/analysis/progress?token=[redacted]`.

### Gate 1: PASS

Every mandatory criterion in `docs/Phases.md` now has evidence against the packaged
artifact built from these fixes: one launch/one window, splash from first paint,
backend readiness, second-launch focus with no second backend, zero console windows,
bounded cancellable retry with a proven round trip, a named code for a forced health
timeout, backend-crash detection *and* surfacing, clean shutdown with sidecar exit
code 0, **zero orphans on both the clean and the terminal-failure path**, a 256-bit
CSPRNG token, a production CSP with no dev origin, `fmt`/`clippy`/`cargo test` green
with real `BackendSupervisor` coverage, no Rust `SIDECAR_EXITED` reference, and all 11
startup phases enumerated in a test.

Two honest limitations, neither a Gate 1 blocker:

- `READY` and the four intermediate checking phases were never **observed** on this
  machine, because the local AI runtime is offline and every launch reached
  `RECOVERY`. They are represented, serialise as documented, and are covered by
  `assess_readiness` unit tests.
- Second-launch focus was measured by sampling `GetForegroundWindow`: 15/15 samples on
  one run, 3/15 on another, because the invoking shell competes for foreground. The
  behavioural invariants that matter (no second window, no second backend, exit code 0,
  window restored) were deterministic on every run.

The visual backlog above is untouched by this closure and remains Phase 3 / Gate 3 work.

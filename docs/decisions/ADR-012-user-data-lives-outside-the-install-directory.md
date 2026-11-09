# ADR-012 — User data lives outside the install directory, and "delete my data" means it

- **Status:** Accepted
- **Date:** 2026-11-09
- **Gate:** 7 (distribution), with a Gate 1 correction
- **Supersedes:** nothing. Extends ADR-010's "the installer is part of the product".

## Decision

The mailbox lives at `%LOCALAPPDATA%\AlfredData`, never in the install
directory. A legacy database is moved there once, by the packaged entry point,
before anything opens it. The uninstaller's "delete app data" checkbox deletes
the real locations, is labelled with what it actually removes, and never
touches Ollama's model store.

## The defect

Tauri's NSIS uninstall template deletes `$LOCALAPPDATA\${BUNDLEID}`, which for
Alfred is `%LOCALAPPDATA%\com.alfred.local` — a directory that has never
existed. Alfred's data is at `%LOCALAPPDATA%\AlfredData`, and on installs
predating this ADR it sat in `%LOCALAPPDATA%\Alfred`, beside the binaries.

So both halves of the user's choice were wrong:

- Tick the box, asking for your mail to be removed: **nothing is deleted.**
- Leave it unticked, asking for your mail to be kept: it survived only because
  the template's `RMDir "$INSTDIR"` has no `/r` and fails while files remain.
  A future template that added `/r` would have silently destroyed the mailbox.

The label made it worse: "Delete the application data" says nothing about a
mailbox going with it.

This was found on 2026-11-09 while reading the generated `installer.nsi`
*before* running an installer over a live install — the install directory
doubling as the data directory was reason enough not to trust it.

## Why the data moved out of the install directory

An installer owns its install directory. Keeping a mailbox there means every
future Tauri upgrade, template change, or repair flow is a potential data-loss
event, and it is the reason the deletion logic had two wrong answers instead of
one. `config.py` already knew this — `_default_database_path` carried a comment
saying new installs use `AlfredData` "so user data can never collide with — or
be swept by — the application install directory" — but nothing migrated the
installs that predated it.

### Migration rules

`migrate_legacy_user_data()` either completes or changes nothing. It never
copies, never partially moves, and never deletes. It declines when:

| Condition | Why |
| --- | --- |
| `ALFRED_DATABASE_PATH` is set | This process is pointed at its own file: a test, a benchmark, a scratch run. |
| No legacy database | Nothing to do. |
| Both databases exist | Ambiguous. Whichever is live is not a migration's business. |
| `-wal` or `-shm` present | The last process did not close cleanly. Renaming a database away from its WAL loses committed transactions, so recovery data is left alone and the next clean start migrates. |
| The rename fails | Including a cross-volume move. The legacy path keeps working. |

The user's own `*.bak` copies travel with the mailbox. The binaries do not.

### One call site, deliberately

Migration is called from `backend/sidecar.py` and nowhere else. It is **not**
reachable from `get_settings()`, because `backend.app.main` binds a Repository
to `settings.database_path` at import time and the test suite reloads that
module. Putting migration behind path resolution meant `pytest` moved the
developer's real mailbox — which is exactly what happened on 2026-11-09 before
this was corrected. `resolve_database_path()` now reports and never moves.

That incident also exposed a pre-existing defect with the same root cause: six
test fixtures unset `ALFRED_DATABASE_PATH` in teardown and then reloaded
`backend.app.main`, binding a Repository to the live mailbox and writing to it.
`conftest.py` existed specifically to prevent this and was being undone.
Fixtures now restore `conftest.SESSION_DATABASE`, and
`test_no_fixture_unsets_the_live_mailbox_guard` forbids the pattern.

## Rejected alternatives

**Point the template's existing branch at the right directory.** Requires
forking Tauri's whole NSIS template to change one line, and every Tauri upgrade
re-inherits the merge. `installerHooks` is the supported seam.

**Fix the checkbox, leave the data where it is.** Makes the choice work while
leaving the mailbox in a directory an installer manages. The colocation is the
root cause, not a detail.

**Delete the data unconditionally on uninstall.** Violates the standing rule
that an upgrade or uninstall must not delete user data without an explicit,
clearly communicated choice.

**Keep the blanket `"installerHooks" not in config` contract.** That test was a
proxy for the real rule. `b44536a` removed a POSTINSTALL hook that re-created
shortcuts from environment-resolved paths, and the ban stopped it returning. The
rule is now stated directly: no install-time hooks, and no shortcut construct in
the one hook that is allowed.

## Verification

| What | How |
| --- | --- |
| Deletion semantics | `tools/release/test_installer_hooks.py` compiles `hooks.nsh` with real `makensis` and **executes** it against a temp directory: ticked deletes, unticked keeps, upgrade keeps, silent uninstall keeps, and the install directory is never wiped recursively. |
| The tests are not decorative | Five mutations of `hooks.nsh` — the original defect included — were each caught by at least one test. |
| Tauri's wiring | `test_tauri_wires_the_hook_into_the_script_it_compiles` reads the generated `installer.nsi` and asserts the `!include`. |
| Migration | 16 tests in `backend/tests/test_legacy_data_migration.py`, every refusal path included. |
| The suite no longer touches the live mailbox | Its SHA-256 was unchanged across three consecutive full runs. |
| Upgrade preserves data | Installed over a live install; the mailbox hash was byte-identical afterwards. |
| The packaged app reads the new location | `sidecar_start … db_path=…\AlfredData\alfred.sqlite3`. |

**Not verified:** a real uninstall with the box ticked, on the shipped
uninstaller. Doing so would delete the actual mailbox on this machine, and
`$LOCALAPPDATA` in NSIS comes from the shell folder, not the environment, so it
cannot be redirected to a scratch location. That direction rests on the
makensis-executed tests of the same file the build compiles. The safe
direction — that nothing is deleted unless asked — is covered both there and
on the real install.

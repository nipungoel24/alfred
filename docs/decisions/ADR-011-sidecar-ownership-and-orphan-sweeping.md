# ADR-011 — A sidecar belongs to one instance, and a sweep never crosses instances

Status: Accepted
Date: 2026-11-06
Gate: 1 (corrects a criterion recorded as PASS)
Companion: `ADR-002-shell-owns-process-lifecycle.md`

## Context

ADR-002 settled that the shell owns the sidecar. It did not say what *owns*
means when more than one shell is running, and the implementation answered that
question badly.

`kill_orphaned_backends(own_port)` ran on every `spawn_and_watch` — every cold
launch and every retry. It listed loopback sockets with `netstat`, then for each
`LISTENING` socket ran `tasklist` to ask whether the holder was an
`alfred-backend`, and killed every match except the one on its own port. Since
the sweep runs *before* the spawn, nothing was ever listening on its own port,
so the exclusion never excluded anything. The effective rule was **kill every
`alfred-backend` on the machine**, including a healthy child legitimately owned
by another live Alfred.

`desktop.log` records the consequence at 2026-10-12T10:26:15–22Z: five
`desktop.start` lines with five distinct PIDs inside three seconds, then
interleaved `backend.killing_orphan`, `sidecar.exited … exit=Some(1)`,
`FATAL_ERROR diag=SIDECAR_EXITED` and respawn, repeating. Each instance killed
the others' children and was killed in turn. A WebView2 failure
(`0x800700AA`, "The requested resource is in use") appears in the same window,
from the instances contending for one user-data folder.

Two further defects sat in the same function:

- Every `netstat`, `tasklist` and `taskkill` was spawned with a bare
  `std::process::Command`. From a `windows_subsystem = "windows"` process, which
  has no console, Windows allocates one for each such child. That is the
  flashing the user reported, and it is a sweep-proportional number of windows:
  one `netstat` plus one `tasklist` per loopback listener, repeated on every
  retry. Gate 1 records "Zero console windows in a release build" as PASS; that
  tick was not supported by the code.
- The `tasklist`-per-socket loop made the cost scale with unrelated local
  services.

## Decision

**A sidecar belongs to the Alfred instance that spawned it. An instance may
terminate only its own child.**

The sweep therefore runs under one precondition: this process is the only live
Alfred. That is the single condition under which every running sidecar must be
an orphan, because our own child is either not spawned yet (cold start) or has
already been stopped by `stop_child()` (restart). Both call paths were verified
to satisfy it.

When another `alfred-desktop` process is alive, the sweep does nothing and logs
`backend.orphan_sweep_skipped`. It is better to leave a stale sidecar for the
next clean launch than to kill a running instance's healthy backend.

Implementation consequences:

1. `kill_orphaned_backends()` takes no port. Ownership, not port identity, is
   the criterion.
2. Process discovery is two `tasklist` calls total — one for `alfred-backend*`,
   one for this executable's own image name — regardless of how many sockets or
   processes exist. `netstat` is no longer used.
3. The instance identifies itself by `std::env::current_exe()`, not a hard-coded
   name, so renaming the binary cannot silently disable sibling detection.
4. Every process spawn goes through `silent_command()`, which sets
   `CREATE_NO_WINDOW` on Windows.
5. The decision is a pure function, `orphan_sweep_plan(backends,
   other_desktops)`, so it is tested without touching a real process. The test
   that previously called `kill_orphaned_backends` directly was removed: under
   the corrected rule it would terminate every real sidecar on the developer's
   machine during `cargo test`.

## Consequences

- Concurrent instances can no longer destroy each other's backends. The failure
  recorded on 2026-10-12 is structurally impossible rather than unlikely.
- A genuine orphan — a sidecar whose Alfred crashed or was force-killed — is
  still cleaned up on the next launch, which is the case the sweep exists for.
- A stale sidecar can survive while a second Alfred is running. It holds a
  loopback port and some memory until the next single-instance launch. This is
  accepted: the sweep is a cleanup convenience, and the port is dynamic, so a
  survivor cannot block a new backend.
- The sweep no longer depends on `netstat` output parsing, which was positional
  and locale-sensitive.

## Rejected

**A Windows Job Object with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`.** This is the
idiomatic answer — the OS kills the child when the parent dies, and no sweep is
needed at all. Rejected *for this change only*: it requires a new `windows`
crate dependency (Rules §8) and replaces a working mechanism rather than
correcting it (Rules §1.2). It is the right long-term design and is recorded as
a Gate 5 candidate, not abandoned.

**An on-disk ownership ledger of `{owner_pid, backend_pid}`.** Rejected: it adds
a persisted file, a write on every spawn, and a stale-entry problem, to answer a
question that "am I the only Alfred?" already answers correctly.

**Reading each process's parent PID.** Rejected: `tasklist` does not report it,
`wmic` is absent on current Windows 11 builds, and shelling out to PowerShell
for `Win32_Process` adds hundreds of milliseconds to the startup path this work
exists to make fast.

**Leaving the sweep out entirely.** Rejected: orphaned sidecars were a real,
observed failure (Gate 1 defect D1), and the shutdown registry that fixed D1
cannot help when the process is killed rather than exiting.

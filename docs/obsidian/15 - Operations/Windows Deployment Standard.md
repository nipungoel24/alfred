---
type: operations
layer: desktop
status: active
tags:
  - windows
  - release
  - deployment
---

# Windows Deployment Standard

Alfred's Windows release contract is:

```text
source commit
→ quality gates
→ sidecar build
→ Tauri release build
→ NSIS installer
→ artifact hashes
→ release manifest
→ human install under the real Windows account
→ read-only install verifier
→ human Start Menu launch
→ app acceptance
```

## Installation model

- Installer: standard Tauri NSIS.
- Install mode: per-user (`currentUser`).
- Install directory: `%LOCALAPPDATA%\Alfred`.
- User data: `%LOCALAPPDATA%\AlfredData` for logs and runtime data; legacy installs may still have `%LOCALAPPDATA%\Alfred\alfred.sqlite3`.
- Logs: `%LOCALAPPDATA%\AlfredData\logs`.
- Uninstall policy for v0.1.0: remove application binaries; preserve user data unless the user explicitly chooses data deletion.

## Shortcut contract

The installer owns Start Menu shortcut creation. Alfred must not package or copy a prebuilt `.lnk` file.

- Start Menu shortcut target: `$INSTDIR\alfred-desktop.exe`.
- Working directory: `$INSTDIR` or empty.
- Shortcut target must be resolved at install time, not build time.
- Forbidden shortcut inputs: build-user `LOCALAPPDATA`, build-user `USERPROFILE`, repository paths, `current_exe()` from the build machine, or agent-generated shortcuts.

## Sidecar contract

The desktop executable and sidecar are deployed together:

```text
%LOCALAPPDATA%\Alfred\alfred-desktop.exe
%LOCALAPPDATA%\Alfred\alfred-backend.exe
```

Tauri `externalBin` resolves the sidecar. Runtime sidecar resolution must not depend on the current working directory, the repository, Python, Node, Cargo, or `backend/.env`.

## Release identity

Every release artifact set must have `release-manifest.json` containing:

- product and version
- Git commit
- target triple
- desktop path, SHA-256, and size
- sidecar path, SHA-256, and size
- installer path, SHA-256, and size

The desktop startup log includes the app version and build commit. Logs must never include runtime tokens, OAuth secrets, or email content.

## Agent sandbox limitation

IDE coding agents may execute Windows commands under a sandbox identity. Agent-side per-user installs and Start Menu shortcuts are not final human evidence.

Agent validation can prove only:

- source builds
- artifacts exist
- static deployment checks pass
- installer-adjacent files contain no runtime-sensitive path leaks

Final release validation requires the human user to install the NSIS installer manually from Explorer, then run:

```powershell
powershell -ExecutionPolicy Bypass -File tools\release\verify_windows_install.ps1
```

Only the human Start Menu launch under the real logged-in account can close installed-startup acceptance.

## Upgrade and rollback

Manual upgrade testing must verify:

- binaries are replaced
- Start Menu shortcut targets the current installation
- `%LOCALAPPDATA%\AlfredData` is preserved
- Gmail credentials, cached mail, tasks, jobs, and history cursor are preserved

Rollback is manual for v0.1.0: uninstall the application, preserve user data, install the previous known-good installer, then run the read-only verifier.

## Signing

Current status: **UNSIGNED DEVELOPMENT RELEASE**.

Do not fake signing, disable SmartScreen, disable Defender, or weaken UAC. External/public distribution requires a trusted Windows code-signing strategy.

# ADR-010 — Google Desktop-app OAuth with PKCE and no client secret

Status: Accepted
Date: 2026-09-26
Gate: 1
Supersedes: nothing. Amends the credential handling described in `README.md` §3 and
`docs/GMAIL_SETUP.md`.

## Context

Alfred authenticates to Gmail with Google OAuth 2.0. The previous build embedded a
Google OAuth **client secret** into the distributed sidecar executable:

```
backend/build_sidecar.py:33-38   staged GMAIL_CLIENT_SECRET into production.env
backend/build_sidecar.py:53-61   PyInstaller --add-data production.env;.
backend/app/config.py:45-55      frozen build reads _MEIPASS/production.env
```

PyInstaller is `--onefile`. It extracts the bundled archive to a temporary directory at
startup, so `production.env` — and therefore the secret — was recoverable by any user who
had the installer. It was also written in the clear to two files on the build machine and
to a third beside the built executable.

Shipping a client secret in a desktop binary is not a matter of obfuscation. It cannot be
made secret.

### What Google's documentation actually says

Verified against Google's own installed-application guide
(<https://developers.google.com/identity/protocols/oauth2/native-app>):

- *"Installed apps are distributed to individual devices, and it is assumed that these
  apps **cannot keep secrets**."*
- The `client_secret` parameter is listed as **Optional** for both the authorization-code
  and refresh-token requests.
- *"In this context, the client secret is obviously not treated as a secret."*
- Recommended client type for Windows desktop: **Desktop app**, with
  `redirect_uri` = `http://localhost`.

Alfred already used PKCE (S256), already used a Desktop-app client, and already omitted
`client_secret` from the token request when it was empty
(`backend/app/mail/providers/gmail.py:53-54`). The secret was therefore **doing nothing
except being distributed**.

## Decision

1. **Alfred ships no Google OAuth client secret.** The build stages only
   `GMAIL_CLIENT_ID`, `OLLAMA_BASE_URL`, and `OLLAMA_MODEL`.
2. **The build fails closed.** `build_sidecar.py` exits non-zero if
   `GMAIL_CLIENT_SECRET` is present in the build environment, and exits non-zero if
   `GMAIL_CLIENT_ID` is missing or still the placeholder.
3. **A frozen build refuses to run with a secret.**
   `backend/app/config.py::_reject_shipped_client_secret` raises at import time, so a
   mis-built artifact is caught on first launch rather than discovered later.
4. **Release artifacts are scanned.** `tools/release/scan_release_secrets.py` inspects the
   built binaries, the installer, and the staged config for a `GOCSPX-` secret, a
   `1//` refresh token, a `ya29.` access token, an `AIza` API key, a `sk-` key, a `gsk_`
   key, a PEM private key, or a `GMAIL_CLIENT_SECRET` assignment.
5. **The Google client ID is intentionally shipped.** It is not a credential: it appears
   in the OAuth consent screen and cannot be used alone. The scanner reports it as `INFO`
   rather than silently ignoring it, so the report stays honest.
6. **Scopes stay read-only**: `userinfo.email` and `gmail.readonly`.

## Consequences

- Alfred stops being a distributor of a Google credential.
- The installed application contains no value that grants access to anything.
- `GMAIL_CLIENT_SECRET` is now a development-only escape hatch. It is never needed for a
  Desktop-app client and should be removed from local `.env` files.
- The scanner is defence in depth, not the primary control. It is a byte-level scan, and a
  PyInstaller archive is compressed, so a clean result on a `.exe` means "nothing in the
  clear", not "nothing inside". The primary controls are (2) and (3), which prevent the
  value from being packaged at all. The tool's own output states this limitation.
- On Windows, users who installed a build that shipped the secret must **reconnect Gmail**;
  see Credential exposure below.

## Credential exposure

The secret has existed on the build machine and inside a locally built sidecar. It has
never been committed: verified with `git log --all -S` for `GOCSPX-`, the Google client
ID, and the legacy `gsk_` key — no real credential appears anywhere in git history.

Artifacts that could contain it, all gitignored and local:

| Path | State |
| --- | --- |
| `build/sidecar-config/production.env` | **purged this session** |
| `desktop/src-tauri/binaries/production.env` | **purged this session** |
| `desktop/src-tauri/binaries/alfred-backend-x86_64-pc-windows-msvc.exe` | built from a secret-bearing config; must be rebuilt |
| `desktop/src-tauri/target/release/alfred-backend.exe` | same |
| `desktop/src-tauri/target/release/bundle/nsis/Alfred_0.1.0_x64-setup.exe` | same |
| `backend/.env`, root `.env` | still contain it; dev-only, never packaged after this change |

### Recommended rotation

1. Revoke the existing client secret in Google Cloud Console.
2. Delete `GMAIL_CLIENT_SECRET` from `backend/.env` and the root `.env`.
3. Rebuild the sidecar and the installer.
4. Run `py tools/release/scan_release_secrets.py` and confirm it exits 0.
5. Discard the previous binaries.

Rotation is only strictly necessary if the previous installer left the build machine. It
did not: the credential was never published. It is still worth doing, because a secret
that has been written in the clear to a world-readable location should be treated as
spent.

## Rejected

**Move the secret to a resource file beside the executable.** Rejected: that is the same
problem with an extra step. The user still receives it.

**Base64 or otherwise obfuscate it.** Rejected: obfuscation is not confidentiality, and
`docs/Rules.md` §1.8 forbids it by name.

**Encrypt the secret with a key shipped alongside it.** Rejected: the key ships too, so
the secret is recoverable. This is the classic "encrypted with a hardcoded key" failure.

**Move the OAuth exchange into the Rust binary.** Rejected: relocating a secret does not
un-distribute it, and it would split the Gmail integration across two languages.

**Use a Google *Web application* client with a real secret held by a server.** Rejected:
that requires a hosted component, which contradicts `docs/PRD.md` §13 non-goal 8 (no
hosted component) and the local-first privacy model.

**Keep the secret and rely on the client ID being public anyway.** Rejected. A published
Desktop-app client secret is a real credential that can be replayed against a Web-type
client, and shipping it converts Alfred from a user of the API into a distributor of it.

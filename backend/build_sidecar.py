"""Build the FastAPI backend executable used by the Windows Tauri bundle.

Usage:
    py backend/build_sidecar.py

Release configuration
---------------------
Only three non-secret values are staged into the frozen executable:

    GMAIL_CLIENT_ID / OLLAMA_BASE_URL / OLLAMA_MODEL

``GMAIL_CLIENT_SECRET`` is deliberately NOT staged and must never be.

Alfred is a desktop application, so it uses a Google OAuth **Desktop app**
client with PKCE. Google's own documentation for installed applications
(https://developers.google.com/identity/protocols/oauth2/native-app) lists
``client_secret`` as **Optional**, and states that for installed apps "the
client secret is obviously not treated as a secret". Shipping one would give
every user a copy of a credential that grants nothing, while turning Alfred
into a distributor of that credential.

The previous version of this script embedded the secret into
``production.env`` and PyInstaller extracted it at runtime, so any user with
the installer could recover a working Google OAuth client. That is fixed
here. See docs/decisions/ADR-010.

Use ``py tools/release/scan_release_secrets.py`` to verify a built artifact
contains no credential.
"""
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "desktop" / "src-tauri" / "binaries"
OUT.mkdir(parents=True, exist_ok=True)

# Non-secret release configuration that is safe to embed in a distributed
# binary. The Google client ID identifies the app; it is not a credential.
EMBEDDABLE_KEYS = ("GMAIL_CLIENT_ID", "OLLAMA_BASE_URL", "OLLAMA_MODEL")

# Keys that must never reach a distributed artifact, whatever the reason.
FORBIDDEN_KEYS = ("GMAIL_CLIENT_SECRET", "GOOGLE_CLIENT_SECRET")

NAME = "alfred-backend-x86_64-pc-windows-msvc"


def _load_build_environment() -> None:
    """Populate the environment from backend/.env when python-dotenv exists."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        print(
            "[build_sidecar] python-dotenv is not installed, so backend/.env "
            "was not read. Values will come from the current shell only.",
            file=sys.stderr,
        )
        return
    load_dotenv(dotenv_path=ROOT / "backend" / ".env")


def main() -> int:
    _load_build_environment()

    leaked = [key for key in FORBIDDEN_KEYS if os.getenv(key)]
    for key in leaked:
        print(
            f"[build_sidecar] REFUSING: {key} is set in the build environment. "
            "Alfred uses a Google Desktop app client with PKCE and must not "
            "ship a client secret. Unset it and rebuild.",
            file=sys.stderr,
        )
    if leaked:
        return 2

    lines = []
    for key in EMBEDDABLE_KEYS:
        value = os.getenv(key)
        if value:
            lines.append(f"{key}={value}")

    client_id = os.getenv("GMAIL_CLIENT_ID", "")
    if not client_id or client_id == "PLACEHOLDER_CLIENT_ID":
        print(
            "[build_sidecar] FAILING: GMAIL_CLIENT_ID is missing or still the "
            "placeholder. A build without it cannot start Google OAuth. Set it "
            "in backend/.env or the shell and rebuild.",
            file=sys.stderr,
        )
        return 3

    staged = ROOT / "build" / "sidecar-config"
    staged.mkdir(parents=True, exist_ok=True)
    staged_env = staged / "production.env"
    staged_env.write_text("\n".join(lines) + "\n", encoding="utf-8")

    command = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--onefile", "--noconsole",
        "--name", NAME,
        "--distpath", str(OUT),
        "--add-data", f"{staged_env};.",
        str(ROOT / "backend" / "sidecar.py"),
    ]
    exit_code = subprocess.call(command, cwd=ROOT)
    if exit_code != 0:
        return exit_code

    # Also keep a copy beside the executable for diagnostics and manual
    # deployment. It holds the same non-secret values that are embedded.
    (OUT / "production.env").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[build_sidecar] built {OUT / (NAME + '.exe')} (no credential embedded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

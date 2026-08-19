"""Build the FastAPI backend executable used by the Windows Tauri bundle.

Usage:
    py backend/build_sidecar.py

Optional build-time configuration (never committed):
    GMAIL_CLIENT_ID / GMAIL_CLIENT_SECRET / OLLAMA_MODEL / OLLAMA_BASE_URL
    are read from the current environment (typically backend/.env in the
    shell session) and written to `production.env` NEXT TO the built
    executable. The frozen sidecar loads that file at runtime, so the
    installed app needs neither the source tree nor backend/.env.
"""
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "desktop" / "src-tauri" / "binaries"
OUT.mkdir(parents=True, exist_ok=True)

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=ROOT / "backend" / ".env")
except ImportError:
    pass

NAME = "alfred-backend-x86_64-pc-windows-msvc"

# Release configuration: embedded into the frozen executable via
# --add-data so the installed app needs neither the source tree nor
# backend/.env. Values come from the build environment (backend/.env).
prod_env_lines = []
for key in ("GMAIL_CLIENT_ID", "GMAIL_CLIENT_SECRET",
            "OLLAMA_BASE_URL", "OLLAMA_MODEL"):
    value = os.getenv(key)
    if value:
        prod_env_lines.append(f"{key}={value}")

if not prod_env_lines or not os.getenv("GMAIL_CLIENT_ID"):
    print("[build_sidecar] WARNING: no GMAIL_CLIENT_ID in environment - "
          "release build will not be able to start Google OAuth until the "
          "sidecar is rebuilt with credentials configured.", file=sys.stderr)

staged = ROOT / "build" / "sidecar-config"
staged.mkdir(parents=True, exist_ok=True)
staged_env = staged / "production.env"
if prod_env_lines:
    staged_env.write_text("\n".join(prod_env_lines) + "\n", encoding="utf-8")
else:
    staged_env.write_text("", encoding="utf-8")

command = [
    sys.executable, "-m", "PyInstaller",
    "--noconfirm", "--onefile", "--noconsole",
    "--name", NAME,
    "--distpath", str(OUT),
    "--add-data", f"{staged_env};.",
    str(ROOT / "backend" / "sidecar.py"),
]
exit_code = subprocess.call(command, cwd=ROOT)

if exit_code == 0:
    # Also keep a copy beside the executable for diagnostics and manual
    # deployment scenarios (config is embedded anyway).
    if prod_env_lines:
        (OUT / "production.env").write_text("\n".join(prod_env_lines) + "\n", encoding="utf-8")
    print(f"[build_sidecar] built {OUT / (NAME + '.exe')} (release config embedded)")

raise SystemExit(exit_code)

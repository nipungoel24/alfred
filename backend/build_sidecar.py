"""Build the FastAPI backend executable used by the Windows Tauri bundle."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "desktop" / "src-tauri" / "binaries"
OUT.mkdir(parents=True, exist_ok=True)
command = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--onefile", "--name", "alfred-backend-x86_64-pc-windows-msvc", "--distpath", str(OUT), str(ROOT / "backend" / "sidecar.py")]
raise SystemExit(subprocess.call(command, cwd=ROOT))

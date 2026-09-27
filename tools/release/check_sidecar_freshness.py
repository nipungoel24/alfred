"""Refuse a release whose packaged sidecar is older than the backend source.

`cargo tauri build` copies whatever sits in `desktop/src-tauri/binaries/`. It
never rebuilds it. So editing the Python backend and then running only
`cargo tauri build` silently packages the *previous* backend - which is exactly
how a release once shipped a sidecar that predated `secure_store.py`, and later
how a sidecar kept using extraction rules that had already been fixed.

This compares the newest backend source against the sidecar artefacts and fails
if any source is newer. It is a check, not a build: rebuilding is
`backend/build_sidecar.py`, and `tools/release/build_release.ps1` runs the two in
the correct order.

Usage:  py -3.12 tools/release/check_sidecar_freshness.py [--quiet]
Exit 0 when fresh, 1 when stale, 2 when there is nothing to compare.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
SIDECAR_DIR = ROOT / "desktop" / "src-tauri" / "binaries"
SIDECAR_NAME = "alfred-backend-x86_64-pc-windows-msvc.exe"
# Paths that legitimately do not ship inside the sidecar.
EXCLUDED_DIRS = {"__pycache__", "tests", ".pytest_cache", "build", "dist", "alembic"}


def backend_sources() -> list[Path]:
    out: list[Path] = []
    for path in BACKEND.rglob("*.py"):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        out.append(path)
    return sorted(out)


def newest_source() -> tuple[Path | None, float]:
    newest: Path | None = None
    newest_mtime = 0.0
    for path in backend_sources():
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue
        if mtime > newest_mtime:
            newest, newest_mtime = path, mtime
    return newest, newest_mtime


def _rel(path: Path) -> str:
    """Repo-relative when possible; absolute paths must not crash the check."""
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def check(quiet: bool = False) -> int:
    sidecar = SIDECAR_DIR / SIDECAR_NAME
    if not sidecar.exists():
        print(f"FAIL  no packaged sidecar at {_rel(sidecar)}")
        print("      run: py -3.12 backend/build_sidecar.py")
        return 1

    newest, newest_mtime = newest_source()
    if newest is None:
        print("FAIL  no backend sources found to compare against")
        return 2

    sidecar_mtime = sidecar.stat().st_mtime
    if sidecar_mtime < newest_mtime:
        rel = _rel(newest)
        print("FAIL  the packaged sidecar is older than the backend source.")
        print(f"      sidecar : {_rel(sidecar)}")
        print(f"      newest  : {rel}")
        print("      A release built now would ship the previous backend.")
        print("      run: py -3.12 backend/build_sidecar.py   (then rebuild the bundle)")
        return 1

    if not quiet:
        print(f"OK    sidecar is current (newest backend source: "
              f"{_rel(newest)})")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    return check(args.quiet)


if __name__ == "__main__":
    sys.exit(main())

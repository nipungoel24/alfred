"""Generate Alfred Windows release artifact manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "desktop/src-tauri/target/release/release-manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def git_commit() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def file_entry(path: Path) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(path)
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "sha256": sha256(path),
        "size": path.stat().st_size,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()

    manifest = {
        "product": "Alfred",
        "version": "0.1.0",
        "git_commit": git_commit(),
        "target": "x86_64-pc-windows-msvc",
        "configuration": "release",
        "desktop": file_entry(ROOT / "desktop/src-tauri/target/release/alfred-desktop.exe"),
        "sidecar": file_entry(ROOT / "desktop/src-tauri/target/release/alfred-backend.exe"),
        "installer": file_entry(
            ROOT
            / "desktop/src-tauri/target/release/bundle/nsis/Alfred_0.1.0_x64-setup.exe"
        ),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

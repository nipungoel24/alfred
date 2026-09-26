"""Scan a built release artifact for embedded credentials.

Alfred must never ship a Google OAuth client secret, an access token, or a
refresh token. A binary is easy to get wrong: PyInstaller extracts bundled
data at runtime, so a value that was "only" in a build directory is still
recoverable from the shipped executable.

This scans the actual release artifacts as opaque byte streams, so it works on
a PE binary without needing to parse or execute it.

Usage:
    py tools/release/scan_release_secrets.py
    py tools/release/scan_release_secrets.py --path some/other/artifact.exe

Exit codes:
    0  clean
    1  at least one pattern matched (a credential is present)
    2  a target file is missing
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Patterns are deliberately specific. A generic "secret" heuristic produces
# false positives on binary data and trains people to ignore the tool.
PATTERNS: list[tuple[str, re.Pattern[bytes]]] = [
    (
        "Google OAuth client secret (GOCSPX- prefix)",
        re.compile(rb"GOCSPX-[A-Za-z0-9_\-]{10,}"),
    ),
    (
        "Google OAuth client secret (1// prefix, legacy)",
        re.compile(rb"1//[A-Za-z0-9_\-]{20,}"),
    ),
    (
        "Google access token (ya29. prefix)",
        re.compile(rb"ya29\.[A-Za-z0-9_\-]{10,}"),
    ),
    (
        "Google API key (AIza prefix)",
        re.compile(rb"AIza[0-9A-Za-z_\-]{30,}"),
    ),
    (
        "Google OAuth client id ending in apps.googleusercontent.com",
        re.compile(rb"[0-9]{6,}-[0-9a-z]{20,}\.apps\.googleusercontent\.com"),
    ),
    (
        "GMAIL_CLIENT_SECRET assignment",
        re.compile(rb"GMAIL_CLIENT_SECRET[=\s]{1,4}[A-Za-z0-9_\-]{10,}"),
    ),
    (
        "OpenAI-style API key (sk- prefix)",
        re.compile(rb"\bsk-[A-Za-z0-9]{20,}"),
    ),
    (
        "Groq API key (gsk_ prefix)",
        re.compile(rb"\bgsk_[A-Za-z0-9]{20,}"),
    ),
    (
        "PEM private key block",
        re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    ),
]

# Findings that are expected in a release artifact and are not credentials.
# The Google client ID identifies the application; it is public information
# that appears in the OAuth consent screen, and Alfred cannot function without
# it. It is reported as INFO so the report is honest, not silent.
EXPECTED_FINDINGS = {
    "Google OAuth client id ending in apps.googleusercontent.com",
}

DEFAULT_TARGETS = [
    "desktop/src-tauri/binaries/alfred-backend-x86_64-pc-windows-msvc.exe",
    "desktop/src-tauri/target/release/alfred-backend.exe",
    "desktop/src-tauri/target/release/alfred-desktop.exe",
    "desktop/src-tauri/target/release/bundle/nsis",
    "desktop/src-tauri/binaries/production.env",
    "build/sidecar-config/production.env",
]

CHUNK = 1024 * 1024
# Patterns are matched against an overlapping window so a value straddling a
# chunk boundary is still found.
OVERLAP = 256


def scan_file(path: Path) -> list[tuple[str, int]]:
    """Return (description, count) for every pattern present in the file."""
    counts: dict[str, int] = {}
    with path.open("rb") as handle:
        tail = b""
        while True:
            chunk = handle.read(CHUNK)
            if not chunk:
                break
            window = tail + chunk
            for description, pattern in PATTERNS:
                found = len(pattern.findall(window))
                if found:
                    counts[description] = counts.get(description, 0) + found
            tail = window[-OVERLAP:]
    return sorted(counts.items())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--path",
        action="append",
        dest="paths",
        help="Artifact file or directory to scan. Repeatable. "
        "Defaults to the known release outputs.",
    )
    args = parser.parse_args(argv)

    targets: list[Path] = []
    if args.paths:
        targets = [Path(p) for p in args.paths]
    else:
        for relative in DEFAULT_TARGETS:
            candidate = ROOT / relative
            if candidate.exists():
                targets.append(candidate)

    if not targets:
        print("No release artifacts found to scan.")
        print("Build the sidecar and installer first, or pass --path.")
        return 2

    missing = [t for t in targets if not t.exists()]
    if missing:
        for path in missing:
            print(f"MISSING  {path}")
        return 2

    blocked: list[str] = []
    for target in targets:
        files = (
            [p for p in target.rglob("*") if p.is_file()]
            if target.is_dir()
            else [target]
        )
        print(f"SCANNING {target.relative_to(ROOT) if target.is_relative_to(ROOT) else target}")
        for file in files:
            findings = scan_file(file)
            if not findings:
                print(f"  clean  {file.name}")
                continue
            for description, count in findings:
                label = "INFO  " if description in EXPECTED_FINDINGS else "SECRET"
                print(f"  {label} {file.name}: {description} x{count}")
                if description not in EXPECTED_FINDINGS:
                    blocked.append(f"{file}: {description}")

    print()
    if blocked:
        print("FAIL: a credential is present in a release artifact.")
        for item in blocked:
            print(f"  - {item}")
        print()
        print("Do not publish this build. Remove the value, rebuild, and rescan.")
        return 1

    print("PASS: no credential found in any scanned release artifact.")
    print()
    print("Scope of this result")
    print("---------------------")
    print("This is a byte-level scan. It is authoritative for plain files such as")
    print("production.env, and it reliably catches a credential written verbatim")
    print("into an uncompressed artifact.")
    print()
    print("It is NOT proof that a PyInstaller --onefile executable is clean.")
    print("PyInstaller compresses the bundled archive, so an embedded value is not")
    print("visible to a raw byte scan. A 'clean' result on a .exe therefore means")
    print("'nothing in the clear', not 'nothing inside'.")
    print()
    print("The authoritative control is that backend/build_sidecar.py refuses to")
    print("stage GMAIL_CLIENT_SECRET at all, and that backend/app/config.py raises")
    print("if a frozen build finds one. See docs/decisions/ADR-010.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

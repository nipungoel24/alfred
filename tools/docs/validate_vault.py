#!/usr/bin/env python3
"""Alfred vault validator: wikilink resolution, canvas JSON validity,
and secret-content scan. Read-only."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
VAULT = ROOT / "docs" / "obsidian"

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")

SUSPICIOUS_PATTERNS = [
    re.compile(r"-----BEGIN (RSA|OPENSSH|EC) PRIVATE KEY"),
    re.compile(r"ya29\.[0-9A-Za-z_-]{20,}"),          # Google access tokens
    re.compile(r"1//[0-9A-Za-z_-]{20,}"),             # Google refresh tokens
    re.compile(r"AKfycb[0-9A-Za-z_-]{20,}"),          # Google API keys
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),            # Google API keys
    re.compile(r"sk-[0-9A-Za-z]{20,}"),               # OpenAI-style keys
    re.compile(r"gsk_[0-9A-Za-z]{20,}"),              # Groq keys
    re.compile(r"client_secret\s*=\s*[\"'][^\"']{10,}[\"']", re.I),
    re.compile(r"BEGIN CERTIFICATE"),
]


def load_notes() -> dict[str, Path]:
    notes: dict[str, Path] = {}
    for p in VAULT.rglob("*.md"):
        notes[p.stem] = p
    return notes


def check_links(notes: dict[str, Path]) -> tuple[int, int, list[str]]:
    resolved, unresolved = 0, 0
    unresolved_list: list[str] = []
    for p in sorted(VAULT.rglob("*.md")):
        text = p.read_text(encoding="utf-8")
        for m in WIKILINK_RE.finditer(text):
            target = m.group(1).strip()
            if target in notes:
                resolved += 1
            else:
                unresolved += 1
                unresolved_list.append(f"{p.relative_to(VAULT)} -> [[{target}]]")
    return resolved, unresolved, unresolved_list


def check_canvases() -> list[str]:
    errors = []
    for p in sorted(VAULT.glob("*.canvas")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"{p.name}: invalid JSON: {e}")
            continue
        if "nodes" not in data or "edges" not in data:
            errors.append(f"{p.name}: missing nodes/edges")
            continue
        node_ids = {n["id"] for n in data["nodes"]}
        for e in data["edges"]:
            if e.get("fromNode") not in node_ids or e.get("toNode") not in node_ids:
                errors.append(f"{p.name}: edge references unknown node")
        for n in data["nodes"]:
            if n.get("type") == "file" and n.get("file"):
                f = n["file"]
                if f.startswith("http"):
                    continue
                if not (VAULT / f).exists():
                    errors.append(f"{p.name}: file node missing: {f}")
    return errors


def scan_secrets() -> list[str]:
    hits = []
    for p in sorted(VAULT.rglob("*.md")):
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pat in SUSPICIOUS_PATTERNS:
            if pat.search(text):
                hits.append(str(p.relative_to(VAULT)))
                break
    return hits


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    notes = load_notes()
    ok = True

    if mode in ("all", "links"):
        resolved, unresolved, unresolved_list = check_links(notes)
        print(f"total_notes={len(notes)}")
        print(f"total_links={resolved + unresolved}")
        print(f"resolved_links={resolved}")
        print(f"unresolved_links={unresolved}")
        for line in unresolved_list[:50]:
            print(f"  {line}")
        if unresolved:
            ok = False

    if mode in ("all", "canvas"):
        errors = check_canvases()
        if errors:
            ok = False
            for e in errors:
                print(f"canvas error: {e}")

    if mode in ("all", "secrets"):
        hits = scan_secrets()
        if hits:
            print("SUSPICIOUS CONTENT (paths only):")
            for h in hits:
                print(f"  {h}")
            ok = False
        else:
            print("secrets: none found")

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

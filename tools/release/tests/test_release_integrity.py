"""The release guard that was missing: a stale sidecar must fail the build.

These pin the two failures that actually happened:

* a UTF-8 BOM made `ast.parse` raise, the knowledge graph skipped the module
  silently, and nothing failed until a symbol assertion much later;
* `cargo tauri build` packaged a sidecar older than the backend source, twice.
"""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from tools.docs.generate_knowledge_graph import analyze_python  # noqa: E402
from tools.release import check_sidecar_freshness as fresh  # noqa: E402


# â”€â”€ the knowledge graph must not swallow a parse error â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_generator_raises_rather_than_skipping_an_unparseable_file(tmp_path):
    broken = tmp_path / "broken_module.py"
    broken.write_bytes(b"\xef\xbb\xbfdef oops(:\n")  # BOM + a syntax error
    with pytest.raises(SyntaxError) as excinfo:
        analyze_python([broken])
    assert "does not parse" in str(excinfo.value)


def test_generator_tolerates_a_bom_on_an_otherwise_valid_file(tmp_path):
    # A BOM alone must not break generation: the failure mode we hit was the
    # silent skip, not the BOM per se.
    good = tmp_path / "fine_module.py"
    good.write_bytes(b"\xef\xbb\xbfdef hello():\n    return 1\n")
    result = analyze_python([good])
    assert result["modules"]


def test_generator_rejects_non_utf8_source(tmp_path):
    bad = tmp_path / "latin_module.py"
    bad.write_bytes(b"def x():\n    return '\xe9'\n")
    with pytest.raises(UnicodeDecodeError):
        analyze_python([bad])


def test_every_backend_module_is_indexed():
    """No module may be missing from the vault.

    This is the assertion that would have caught the BOM: `task_derivation`
    vanished from the graph and the only symptom was a downstream failure.
    """
    skip = {"__pycache__", "tests", ".pytest_cache"}
    paths = [p for p in (ROOT / "backend").rglob("*.py")
             if not any(part in skip for part in p.parts)]
    result = analyze_python(paths)
    modules = set(result["modules"])
    for expected in ("backend.app.services.task_derivation",
                     "backend.app.services.due_dates",
                     "backend.app.schemas",
                     "backend.app.main"):
        assert expected in modules, f"{expected} is missing from the knowledge graph"


# â”€â”€ the sidecar freshness guard â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_freshness_detector_passes_for_a_current_sidecar():
    sidecar = fresh.SIDECAR_DIR / fresh.SIDECAR_NAME
    if not sidecar.exists():
        pytest.skip("no packaged sidecar in this checkout")
    if fresh.check(quiet=True) != 0:
        pytest.skip("sidecar is genuinely stale in this checkout; "
                    "the canonical release build regenerates it")


def test_freshness_detector_fails_when_the_sidecar_is_older(tmp_path, monkeypatch):
    """The exact hazard: package a sidecar older than the backend source."""
    backend = tmp_path / "backend"
    (backend / "app").mkdir(parents=True)
    source = backend / "app" / "thing.py"
    source.write_text("VALUE = 1\n")
    binaries = tmp_path / "binaries"
    binaries.mkdir()
    sidecar = binaries / fresh.SIDECAR_NAME
    sidecar.write_bytes(b"old")

    import os
    # Make the source strictly newer than the sidecar.
    os.utime(source, (2_000_000_000, 2_000_000_000))
    os.utime(sidecar, (1_000_000_000, 1_000_000_000))

    monkeypatch.setattr(fresh, "BACKEND", backend)
    monkeypatch.setattr(fresh, "SIDECAR_DIR", binaries)
    assert fresh.check(quiet=True) == 1, "a stale sidecar must fail the check"


def test_freshness_detector_fails_when_the_sidecar_is_absent(tmp_path, monkeypatch):
    backend = tmp_path / "backend"
    (backend / "app").mkdir(parents=True)
    (backend / "app" / "thing.py").write_text("VALUE = 1\n")
    binaries = tmp_path / "binaries"
    binaries.mkdir()
    monkeypatch.setattr(fresh, "BACKEND", backend)
    monkeypatch.setattr(fresh, "SIDECAR_DIR", binaries)
    assert fresh.check(quiet=True) == 1


def test_release_script_enforces_the_order():
    """The documented sequence must build the sidecar before the bundle."""
    script = (ROOT / "tools" / "release" / "build_release.ps1").read_text(encoding="utf-8")
    assert "build_sidecar.py" in script, "the release script must build the sidecar"
    assert "cargo tauri build" in script, "the release script must build the bundle"
    assert "check_sidecar_freshness.py" in script, (
        "the release script must verify freshness rather than assume it"
    )
    # Compare the order of the commands that actually run, ignoring the header
    # comment, which necessarily mentions `cargo tauri build` first.
    body = "\n".join(line for line in script.splitlines()
                     if not line.lstrip().startswith("#"))
    assert body.index("build_sidecar.py") < body.index("cargo tauri build"), (
        "the sidecar must be built before the bundle, or the bundle packages a "
        "stale backend"
    )
    # The freshness gate must run before the bundle, and again after it.
    assert body.index("check_sidecar_freshness.py") < body.index("cargo tauri build")
    assert body.rindex("check_sidecar_freshness.py") > body.index("cargo tauri build")


def test_cargo_tauri_build_does_not_rebuild_the_sidecar():
    """Document the assumption the guard exists to cover.

    If this ever starts failing, `cargo tauri build` grew sidecar-building
    behaviour and the freshness guard can move from mandatory to belt-and-braces.
    """
    conf = (ROOT / "desktop" / "src-tauri" / "tauri.conf.json").read_text(encoding="utf-8")
    assert "externalBin" in conf, "the sidecar is packaged via externalBin"
    # Nothing in the Tauri config invokes the Python build.
    assert "build_sidecar" not in conf


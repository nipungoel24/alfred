"""Compiles and EXECUTES desktop/src-tauri/installer/hooks.nsh (ADR-012).

The static contracts in check_windows_deployment.py read the hook; these run
it. NSIS compiles the real file into a throwaway silent installer whose only
section sets the two guard variables and inserts NSIS_HOOK_POSTUNINSTALL,
with ALFRED_DATA_DIR pointed at a temporary directory. The filesystem
afterwards is the assertion.

That matters because the behaviour under test is irreversible deletion of a
user's mail, and the alternative — reviewing the macro and trusting it — is
how the defect in ADR-012 survived in the first place: the checkbox looked
correct and deleted nothing.

Skipped off Windows and wherever makensis is unavailable.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
HOOKS = ROOT / "desktop/src-tauri/installer/hooks.nsh"


def _find_makensis() -> Path | None:
    """Locate NSIS without baking a build-machine path into the repo.

    check_windows_deployment.test_no_runtime_sensitive_user_paths_in_release_sources
    forbids a hardcoded user path here, so this resolves at runtime.
    """
    explicit = os.environ.get("NSIS_PATH", "").strip()
    if explicit:
        candidate = Path(explicit)
        candidate = candidate if candidate.is_file() else candidate / "makensis.exe"
        if candidate.is_file():
            return candidate

    local_app_data = os.environ.get("LOCALAPPDATA", "").strip()
    if local_app_data:
        # Where the Tauri CLI puts the toolchain it downloads.
        bundled = Path(local_app_data) / "tauri" / "NSIS" / "makensis.exe"
        if bundled.is_file():
            return bundled

    found = shutil.which("makensis")
    return Path(found) if found else None


MAKENSIS = _find_makensis()

pytestmark = [
    pytest.mark.skipif(sys.platform != "win32", reason="NSIS is Windows-only"),
    pytest.mark.skipif(MAKENSIS is None, reason="makensis not available"),
]


HARNESS = """\
Unicode true
RequestExecutionLevel user
SilentInstall silent
OutFile "{out}"
InstallDir "{install_dir}"

!include LogicLib.nsh

; Declared by Tauri's installer template, which this harness stands in for.
Var DeleteAppDataCheckboxState
Var UpdateMode

!define ALFRED_DATA_DIR "{data_dir}"
!include "{hooks}"

Section
  StrCpy $INSTDIR "{install_dir}"
  StrCpy $DeleteAppDataCheckboxState "{checkbox}"
  StrCpy $UpdateMode "{update_mode}"
  !insertmacro NSIS_HOOK_POSTUNINSTALL
SectionEnd
"""


def _layout(tmp_path: Path) -> tuple[Path, Path]:
    """A legacy install: binaries, mailbox and backups in the install dir."""
    install_dir = tmp_path / "Alfred"
    data_dir = tmp_path / "AlfredData"
    (install_dir / "nested").mkdir(parents=True)
    (data_dir / "logs").mkdir(parents=True)

    (install_dir / "alfred-desktop.exe").write_bytes(b"MZ shell")
    (install_dir / "alfred-backend.exe").write_bytes(b"MZ sidecar")
    (install_dir / "alfred.sqlite3").write_bytes(b"legacy mailbox")
    (install_dir / "alfred.sqlite3-wal").write_bytes(b"wal")
    (install_dir / "alfred.sqlite3-shm").write_bytes(b"shm")
    (install_dir / "alfred.sqlite3.20260927-pre.bak").write_bytes(b"backup")
    (install_dir / "nested" / "keep.txt").write_bytes(b"not mine to delete")

    (data_dir / "alfred.sqlite3").write_bytes(b"managed mailbox")
    (data_dir / "logs" / "backend.log").write_bytes(b"log line")
    return install_dir, data_dir


def _run_hook(tmp_path: Path, *, checkbox: str, update_mode: str) -> tuple[Path, Path]:
    install_dir, data_dir = _layout(tmp_path)
    out = tmp_path / "harness.exe"
    script = tmp_path / "harness.nsi"
    script.write_text(
        HARNESS.format(
            out=out,
            install_dir=install_dir,
            data_dir=data_dir,
            hooks=HOOKS,
            checkbox=checkbox,
            update_mode=update_mode,
        ),
        encoding="utf-8",
    )

    compiled = subprocess.run(
        [str(MAKENSIS), "/V2", str(script)],
        capture_output=True, text=True,
    )
    assert compiled.returncode == 0, (
        f"makensis failed:\n{compiled.stdout}\n{compiled.stderr}"
    )

    executed = subprocess.run([str(out), "/S"], capture_output=True, text=True)
    assert executed.returncode == 0, f"harness failed: {executed.stdout}"
    return install_dir, data_dir


def _assert_intact(path: Path, expected: bytes) -> None:
    assert path.exists(), f"{path.name} was deleted and should have been kept"
    assert path.read_bytes() == expected


def test_a_ticked_checkbox_really_deletes_the_mail(tmp_path):
    install_dir, data_dir = _run_hook(tmp_path, checkbox="1", update_mode="0")

    assert not data_dir.exists(), "AlfredData survived a ticked checkbox"
    assert not (install_dir / "alfred.sqlite3").exists()
    assert not (install_dir / "alfred.sqlite3-wal").exists()
    assert not (install_dir / "alfred.sqlite3-shm").exists()
    assert list(install_dir.glob("*.bak")) == []


def test_deletion_does_not_reach_beyond_the_users_data(tmp_path):
    """The install directory is not wiped recursively.

    The binaries are the uninstaller's to remove by name; a subdirectory is
    nobody's business here. A `RMDir /r "$INSTDIR"` would take both.
    """
    install_dir, _ = _run_hook(tmp_path, checkbox="1", update_mode="0")

    _assert_intact(install_dir / "alfred-desktop.exe", b"MZ shell")
    _assert_intact(install_dir / "alfred-backend.exe", b"MZ sidecar")
    _assert_intact(install_dir / "nested" / "keep.txt", b"not mine to delete")


def test_an_unticked_checkbox_keeps_everything(tmp_path):
    install_dir, data_dir = _run_hook(tmp_path, checkbox="0", update_mode="0")

    _assert_intact(data_dir / "alfred.sqlite3", b"managed mailbox")
    assert (data_dir / "logs" / "backend.log").exists()
    _assert_intact(install_dir / "alfred.sqlite3", b"legacy mailbox")
    assert (install_dir / "alfred.sqlite3.20260927-pre.bak").exists()


def test_an_upgrade_keeps_everything_even_with_the_box_ticked(tmp_path):
    """The upgrade path runs the old uninstaller to clear binaries only."""
    install_dir, data_dir = _run_hook(tmp_path, checkbox="1", update_mode="1")

    _assert_intact(data_dir / "alfred.sqlite3", b"managed mailbox")
    _assert_intact(install_dir / "alfred.sqlite3", b"legacy mailbox")


def test_a_silent_uninstall_keeps_everything(tmp_path):
    """The confirmation page never runs, so the variable is never set.

    An unset NSIS variable is the empty string. Deleting a mailbox requires
    a choice, and no choice was made here.
    """
    install_dir, data_dir = _run_hook(tmp_path, checkbox="", update_mode="0")

    _assert_intact(data_dir / "alfred.sqlite3", b"managed mailbox")
    _assert_intact(install_dir / "alfred.sqlite3", b"legacy mailbox")


GENERATED_SCRIPT = (
    ROOT / "desktop/src-tauri/target/release/nsis/x64/installer.nsi"
)


@pytest.mark.skipif(
    not GENERATED_SCRIPT.exists(),
    reason="no NSIS script generated yet; run tools/release/build_release.ps1",
)
def test_tauri_wires_the_hook_into_the_script_it_compiles():
    """The last link: Tauri must actually include the file.

    The macro being correct is useless if `installerHooks` is misspelled or
    the path is wrong — `!ifmacrodef` would quietly be false and the build
    would succeed with no hook at all, which is the same shape of silent
    no-op as the defect in ADR-012.

    Compilation proves the rest: makensis errors on a bad `!include`, and
    the tests above insert NSIS_HOOK_POSTUNINSTALL by that exact name.
    """
    script = GENERATED_SCRIPT.read_text(encoding="utf-8", errors="ignore")
    includes = [
        line for line in script.splitlines()
        if line.strip().startswith("!include") and "installer" in line
        and "hooks.nsh" in line
    ]
    assert includes, "Tauri did not include installer/hooks.nsh"
    assert "!insertmacro NSIS_HOOK_POSTUNINSTALL" in script

    language = ROOT / "desktop/src-tauri/target/release/nsis/x64/English.nsh"
    if language.exists():
        label = language.read_text(encoding="utf-8", errors="ignore")
        assert "Delete the application data" not in label
        assert "Delete my downloaded mail" in label

"""Static Windows deployment contract checks for Alfred.

These checks intentionally inspect source and generated installer-adjacent files
without installing the app. They prevent build-user paths and shortcut-repair
mechanisms from becoming part of the release contract.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_RUNTIME_PATHS = (
    "CodexSandboxOffline",
    r"C:\Users\Nipun",
)
SOURCE_GLOBS = (
    "desktop/src-tauri/tauri.conf.json",
    "desktop/src-tauri/src/**/*.rs",
    "desktop/src-tauri/*.nsh",
    "desktop/src-tauri/*.nsi",
    "backend/**/*.py",
    "frontend/src/**/*",
    "tools/release/**/*",
)


def _iter_files() -> list[Path]:
    files: list[Path] = []
    for pattern in SOURCE_GLOBS:
        files.extend(
            p
            for p in ROOT.glob(pattern)
            if p.is_file()
            and "__pycache__" not in p.parts
            and p.name != "check_windows_deployment.py"
        )
    return sorted(set(files))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def test_no_custom_nsis_shortcut_repair_hook() -> None:
    config = _read(ROOT / "desktop/src-tauri/tauri.conf.json")
    assert "installerHooks" not in config
    assert not (ROOT / "desktop/src-tauri/nsis-hooks.nsh").exists()


def test_no_prebuilt_shortcuts_are_bundled() -> None:
    bundled_links = [
        p
        for p in ROOT.rglob("*.lnk")
        if "node_modules" not in p.parts and "target" not in p.parts
    ]
    assert bundled_links == []


def test_no_runtime_sensitive_user_paths_in_release_sources() -> None:
    offenders: list[str] = []
    for path in _iter_files():
        text = _read(path)
        for needle in FORBIDDEN_RUNTIME_PATHS:
            if needle in text:
                offenders.append(f"{path.relative_to(ROOT)}: {needle}")
        # Hardcoded C:\Users\<name> in release/runtime code is a deployment smell.
        if re.search(r"C:\\Users\\[A-Za-z0-9_.-]+", text):
            offenders.append(f"{path.relative_to(ROOT)}: hardcoded C:\\Users path")
    assert offenders == []


def test_tauri_uses_standard_per_user_nsis_and_external_sidecar() -> None:
    config = _read(ROOT / "desktop/src-tauri/tauri.conf.json")
    assert '"targets": "nsis"' in config
    assert '"installMode": "currentUser"' in config
    assert '"externalBin": ["binaries/alfred-backend"]' in config
    assert "installerHooks" not in config


def test_frontend_packaged_tauri_does_not_fall_back_to_dev_port() -> None:
    client = _read(ROOT / "frontend/src/api/client.ts")
    tauri_branch = client.split("if (isTauri())", 1)[1].split("BASE = import.meta", 1)[0]
    assert "http://127.0.0.1:8765" not in tauri_branch
    assert "await_backend_ready" in tauri_branch


def test_sidecar_resolution_uses_tauri_external_bin_not_cwd() -> None:
    main = _read(ROOT / "desktop/src-tauri/src/main.rs")
    assert '.sidecar("alfred-backend")' in main
    # Check that the sidecar spawn function doesn't use current_dir
    spawn_section = main.split("fn spawn_and_watch", 1)[1].split("fn http_request", 1)[0] if "fn spawn_and_watch" in main else main.split("fn spawn_backend", 1)[1].split("fn http_request", 1)[0]
    assert "current_dir" not in spawn_section


def test_build_identity_is_logged() -> None:
    build_rs = _read(ROOT / "desktop/src-tauri/build.rs")
    main = _read(ROOT / "desktop/src-tauri/src/main.rs")
    assert "ALFRED_GIT_COMMIT" in build_rs
    assert "ALFRED_GIT_COMMIT" in main

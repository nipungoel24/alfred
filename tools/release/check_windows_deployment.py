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


def test_build_stamp_is_invalidated_when_git_head_moves() -> None:
    """The embedded commit must match the tree that was actually built.

    `build.rs` reads `git rev-parse HEAD`, but Cargo caches a build script's
    output unless the script declares what it depends on. With no directive,
    Cargo re-ran it only when a file inside `desktop/src-tauri` changed, so a
    commit touching only `docs/` or `tools/` left the *previous* commit compiled
    into `ALFRED_GIT_COMMIT` and the shell logged a build identity that did not
    describe the running artifact.
    """
    build_rs = _read(ROOT / "desktop/src-tauri/build.rs")
    assert "cargo:rerun-if-changed" in build_rs, (
        "build.rs must declare its inputs or the embedded commit goes stale"
    )
    assert ".git" in build_rs and "HEAD" in build_rs, (
        "the rerun trigger must track the repository HEAD"
    )


def test_startup_phase_log_field_is_not_named_code() -> None:
    """The lifecycle diagnostic must survive the global redactor.

    `redact()` treats a bare `code=` as an OAuth authorization code, because
    uvicorn's access log really does contain `?code=` on the OAuth callback. A
    `startup.phase ... code=` field was therefore rewritten to `code=[redacted]`
    on every transition, deleting the support surface the diagnostic codes
    exist to provide. The field is `diag=` now.
    """
    main = _read(ROOT / "desktop/src-tauri/src/main.rs")
    body = _strip_rust_comments(main)
    assert "startup.phase phase={} diag={}" in body, (
        "startup.phase must log its diagnostic as diag=, not code="
    )
    assert "startup.phase phase={} code={}" not in body, (
        "a bare code= field is stripped by the redactor"
    )


def test_a_terminal_failure_does_not_release_child_ownership() -> None:
    """Exit-time termination must keep a target after a startup failure.

    The poller used to clear the shutdown registry on a terminal failure. A
    terminal failure does not mean the child died — a hung backend is still
    running — so `terminate()` found an empty slot and left live
    `alfred-backend.exe` processes behind.
    """
    main = _read(ROOT / "desktop/src-tauri/src/main.rs")
    poller = main.split("Generation-guarded readiness polling.", 1)[-1]
    settle = main.split("fn settle_poll_outcome", 1)[-1].split("\n}", 1)[0]
    assert "registry" not in settle, (
        "settle_poll_outcome must not touch the shutdown registry"
    )
    # The poller resolves through the helper rather than clearing the registry.
    assert "settle_poll_outcome(phase, port, token)" in poller
    assert "registry_poll.clear()" not in poller, (
        "the poller must not release ownership of a possibly-live child"
    )


# ── Credential containment ─────────────────────────────────────────
#
# Alfred authenticates as a Google Desktop app client with PKCE, for which
# Google's documentation lists client_secret as optional. A packaged build
# must therefore never contain one. These checks are the static half of that
# rule; tools/release/scan_release_secrets.py is the artifact half.


def test_sidecar_builder_never_stages_a_client_secret() -> None:
    builder = _read(ROOT / "backend/build_sidecar.py")
    # The key may appear in FORBIDDEN_KEYS, but never in the embeddable list.
    embeddable = builder.split("EMBEDDABLE_KEYS", 1)[1].split(")", 1)[0]
    assert "GMAIL_CLIENT_SECRET" not in embeddable
    assert "GMAIL_CLIENT_ID" in embeddable


def test_sidecar_builder_refuses_to_build_with_a_client_secret() -> None:
    builder = _read(ROOT / "backend/build_sidecar.py")
    assert "FORBIDDEN_KEYS" in builder
    assert "GMAIL_CLIENT_SECRET" in builder
    # It must be a hard failure, not a warning that lets the build proceed.
    assert "REFUSING" in builder


def test_frozen_build_rejects_a_client_secret() -> None:
    config = _read(ROOT / "backend/app/config.py")
    assert "_reject_shipped_client_secret" in config
    # The guard must raise rather than warn.
    assert "raise RuntimeError" in config


def test_release_secret_scanner_exists_and_covers_known_patterns() -> None:
    scanner_path = ROOT / "tools/release/scan_release_secrets.py"
    assert scanner_path.exists(), "release artifact secret scan must exist"
    scanner = _read(scanner_path)
    for pattern in ("GOCSPX-", "ya29", "AIza", "GMAIL_CLIENT_SECRET", "PRIVATE KEY"):
        assert pattern in scanner, f"scanner must detect {pattern}"


def test_staged_release_config_on_disk_has_no_secret() -> None:
    """The files the builder stages must not hold a credential right now."""
    offenders: list[str] = []
    for relative in (
        "build/sidecar-config/production.env",
        "desktop/src-tauri/binaries/production.env",
    ):
        path = ROOT / relative
        if not path.exists():
            continue
        for line in _read(path).splitlines():
            if line.startswith("GMAIL_CLIENT_SECRET="):
                offenders.append(relative)
    assert offenders == [], f"client secret present in {offenders}"


# ── Startup lifecycle ──────────────────────────────────────────────


def test_main_window_is_created_visible() -> None:
    """A hidden window with no reveal on the cold path means Alfred never
    appears. The window must be visible at creation, and the reveal helper
    must exist as the single authoritative path."""
    config = _read(ROOT / "desktop/src-tauri/tauri.conf.json")
    assert '"visible": true' in config, "main window must be created visible"
    main = _read(ROOT / "desktop/src-tauri/src/main.rs")
    assert "fn reveal_main_window" in main


def test_reveal_is_not_confined_to_the_single_instance_callback() -> None:
    main = _read(ROOT / "desktop/src-tauri/src/main.rs")
    # The cold launch must reveal from setup and/or RunEvent::Ready, not only
    # from the second-launch path.
    assert "reveal_main_window(&handle)" in main
    assert "tauri::RunEvent::Ready" in main


def test_production_csp_has_no_development_origin() -> None:
    """`devUrl` may name the Vite dev server; the shipped CSP may not.

    Only the `csp` directive is checked. A blanket search for the dev origin
    would flag the legitimate dev configuration.
    """
    config = _read(ROOT / "desktop/src-tauri/tauri.conf.json")
    csp_line = next(
        (line for line in config.splitlines() if '"csp"' in line),
        None,
    )
    assert csp_line is not None, "tauri.conf.json must declare a CSP"
    for origin in ("localhost:5173", "127.0.0.1:5173"):
        assert origin not in csp_line, f"production CSP must not allow {origin}"


def test_session_token_comes_from_the_os_csprng() -> None:
    main = _read(ROOT / "desktop/src-tauri/src/main.rs")
    assert "getrandom::getrandom" in main
    # The old clock+PID derivation must be gone from the function body.
    # Comments may still name it for historical reasons.
    body = _strip_rust_comments(main).split("fn generate_token", 1)[1].split("\n}", 1)[0]
    for banned in ("RandomState", "build_hasher", "SystemTime", "process::id"):
        assert banned not in body, f"token must not be derived from {banned}"


def test_readiness_is_protocol_based_not_a_substring_match() -> None:
    main = _read(ROOT / "desktop/src-tauri/src/main.rs")
    assert 'response.contains("200")' not in main
    # It must parse the status line and require a JSON content type.
    assert "content_type" in main
    assert "application/json" in main


def _strip_rust_comments(text: str) -> str:
    """Remove `//` line comments so checks test code, not prose.

    Alfred's source explains the defects it fixed in comments; a naive
    substring search would then flag the explanation of the bug as the bug.
    """
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        lines.append(line.split("//", 1)[0])
    return "\n".join(lines)


def test_exit_does_not_depend_on_winning_a_lock_race() -> None:
    main = _read(ROOT / "desktop/src-tauri/src/main.rs")
    assert "registry.terminate()" in main
    # try_lock must not appear in executable code in the run loop.
    run_loop = main.split("app.run(", 1)[1]
    assert "try_lock" not in _strip_rust_comments(run_loop)


def test_session_token_is_never_logged() -> None:
    main = _read(ROOT / "desktop/src-tauri/src/main.rs")
    # No log statement may interpolate the token variable.
    for line in _strip_rust_comments(main).splitlines():
        stripped = line.strip()
        if stripped.startswith(("log::", "println!")) and "token" in stripped:
            assert "redact" in stripped, f"token may reach the log: {stripped}"


def test_credential_store_is_fail_closed() -> None:
    store = _read(ROOT / "backend/app/db/secure_store.py")
    assert "SecureStoreUnavailable" in store
    # The reversible fallback must be gone from the write path.
    encrypt_section = store.split("def encrypt_token", 1)[1].split("def decrypt_token", 1)[0]
    assert "b64encode" not in encrypt_section
    # ctypes.BYTE was removed in Python 3.12 and silently disabled DPAPI.
    # Check the struct field, not the history note that mentions it.
    assert "POINTER(ctypes.BYTE)" not in store
    assert "POINTER(ctypes.c_ubyte)" in store

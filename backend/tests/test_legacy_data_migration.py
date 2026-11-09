"""Moving a legacy mailbox out of the install directory (ADR-012).

Every refusal matters as much as the move: this code runs on startup against
a real mailbox, and the rule is that it either completes or changes nothing.
The tests drive %LOCALAPPDATA% through monkeypatch, so they are
platform-neutral and never touch the developer's own data.
"""

from pathlib import Path
import logging

import pytest

from backend.app import config


LEGACY_BYTES = b"legacy mailbox contents"


@pytest.fixture
def local_app_data(tmp_path, monkeypatch) -> Path:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.delenv("ALFRED_DATABASE_PATH", raising=False)
    return tmp_path


def _make_legacy(root: Path, *, backups: int = 0, sidecars: tuple[str, ...] = ()) -> Path:
    install_dir = root / "Alfred"
    install_dir.mkdir(parents=True, exist_ok=True)
    # The binaries the installer owns, which must never be mistaken for data.
    (install_dir / "alfred-desktop.exe").write_bytes(b"MZ shell")
    (install_dir / "alfred-backend.exe").write_bytes(b"MZ sidecar")
    db = install_dir / "alfred.sqlite3"
    db.write_bytes(LEGACY_BYTES)
    for n in range(backups):
        (install_dir / f"alfred.sqlite3.2026092{n}-pre.bak").write_bytes(
            f"backup {n}".encode()
        )
    for suffix in sidecars:
        (install_dir / f"alfred.sqlite3{suffix}").write_bytes(b"wal frame")
    return db


def test_a_legacy_mailbox_moves_into_alfreddata(local_app_data):
    legacy = _make_legacy(local_app_data)

    moved_to = config.migrate_legacy_user_data()

    assert moved_to == local_app_data / "AlfredData"
    assert not legacy.exists()
    managed = local_app_data / "AlfredData" / "alfred.sqlite3"
    assert managed.read_bytes() == LEGACY_BYTES


def test_the_users_own_backups_travel_with_the_mailbox(local_app_data):
    _make_legacy(local_app_data, backups=3)

    config.migrate_legacy_user_data()

    managed_dir = local_app_data / "AlfredData"
    assert sorted(p.name for p in managed_dir.glob("*.bak")) == [
        "alfred.sqlite3.20260920-pre.bak",
        "alfred.sqlite3.20260921-pre.bak",
        "alfred.sqlite3.20260922-pre.bak",
    ]
    assert list((local_app_data / "Alfred").glob("*.bak")) == []


def test_the_installed_binaries_are_left_where_they_are(local_app_data):
    _make_legacy(local_app_data, backups=1)

    config.migrate_legacy_user_data()

    install_dir = local_app_data / "Alfred"
    assert (install_dir / "alfred-desktop.exe").read_bytes() == b"MZ shell"
    assert (install_dir / "alfred-backend.exe").read_bytes() == b"MZ sidecar"
    assert not (local_app_data / "AlfredData" / "alfred-desktop.exe").exists()


def test_nothing_happens_when_there_is_no_legacy_mailbox(local_app_data):
    (local_app_data / "AlfredData").mkdir()

    assert config.migrate_legacy_user_data() is None
    assert not (local_app_data / "AlfredData" / "alfred.sqlite3").exists()


def test_an_unclean_shutdown_defers_the_move(local_app_data, caplog):
    """A `-wal` beside the database means unrecovered transactions.

    Renaming the database away from its WAL loses them, so the migration
    waits for a clean start instead.
    """
    legacy = _make_legacy(local_app_data, sidecars=("-wal", "-shm"))

    with caplog.at_level(logging.WARNING, logger="alfred.storage"):
        assert config.migrate_legacy_user_data() is None

    assert legacy.read_bytes() == LEGACY_BYTES
    assert not (local_app_data / "AlfredData" / "alfred.sqlite3").exists()
    assert "reason=unclean_shutdown" in caplog.text


@pytest.mark.parametrize("sidecar", ["-wal", "-shm"])
def test_either_sidecar_alone_defers_the_move(local_app_data, sidecar):
    legacy = _make_legacy(local_app_data, sidecars=(sidecar,))

    assert config.migrate_legacy_user_data() is None
    assert legacy.exists()


def test_two_databases_are_left_alone(local_app_data, caplog):
    legacy = _make_legacy(local_app_data)
    managed_dir = local_app_data / "AlfredData"
    managed_dir.mkdir()
    (managed_dir / "alfred.sqlite3").write_bytes(b"managed mailbox")

    with caplog.at_level(logging.WARNING, logger="alfred.storage"):
        assert config.migrate_legacy_user_data() is None

    assert legacy.read_bytes() == LEGACY_BYTES
    assert (managed_dir / "alfred.sqlite3").read_bytes() == b"managed mailbox"
    assert "reason=both_present" in caplog.text


def test_a_failed_move_keeps_the_mailbox_readable(local_app_data, monkeypatch, caplog):
    """If the rename fails the app must still find its data.

    The legacy path is returned, so the user loses nothing but a log line.
    """
    legacy = _make_legacy(local_app_data)

    def refuse(src, dst):
        raise OSError("simulated cross-volume move")

    monkeypatch.setattr(config.os, "replace", refuse)

    with caplog.at_level(logging.WARNING, logger="alfred.storage"):
        assert config.migrate_legacy_user_data() is None

    assert legacy.read_bytes() == LEGACY_BYTES
    assert "legacy_migration_failed" in caplog.text
    assert config.resolve_database_path() == legacy


def test_migration_is_not_attempted_twice(local_app_data):
    _make_legacy(local_app_data)

    assert config.migrate_legacy_user_data() == local_app_data / "AlfredData"
    assert config.migrate_legacy_user_data() is None


def test_resolve_reports_the_new_location_once_migration_has_run(local_app_data):
    """`resolve_database_path` does not migrate; it reports.

    Migration has exactly one call site, in backend/sidecar.py. Anything
    reachable from `get_settings()` runs during pytest against real paths —
    which is how the 2026-11-09 suite run moved the live mailbox.
    """
    legacy = _make_legacy(local_app_data)

    assert config.resolve_database_path() == legacy

    config.migrate_legacy_user_data()

    resolved = config.resolve_database_path()
    assert resolved == local_app_data / "AlfredData" / "alfred.sqlite3"
    assert resolved.exists()


def test_resolving_the_path_never_moves_anything(local_app_data):
    legacy = _make_legacy(local_app_data, backups=1)

    for _ in range(3):
        config.resolve_database_path()

    assert legacy.read_bytes() == LEGACY_BYTES
    assert not (local_app_data / "AlfredData").exists()


def test_a_fresh_install_resolves_to_alfreddata_without_creating_anything(local_app_data):
    resolved = config.resolve_database_path()

    assert resolved == local_app_data / "AlfredData" / "alfred.sqlite3"
    assert not (local_app_data / "Alfred").exists()


def test_an_explicit_database_path_never_moves_user_data(local_app_data, monkeypatch):
    """A scratch or test run must leave the real mailbox untouched.

    The old expression passed `_default_database_path()` as `os.getenv`'s
    default, so it ran even when the override was set. That was harmless
    while it was pure; with migration attached it would move the user's mail
    out from under a scratch run.
    """
    legacy = _make_legacy(local_app_data)
    scratch = local_app_data / "scratch.sqlite3"
    monkeypatch.setenv("ALFRED_DATABASE_PATH", str(scratch))

    assert config.resolve_database_path() == scratch
    # The guard inside the migration itself, independent of the call site.
    assert config.migrate_legacy_user_data() is None
    assert legacy.read_bytes() == LEGACY_BYTES
    assert not (local_app_data / "AlfredData").exists()


def test_a_blank_override_is_treated_as_absent(local_app_data, monkeypatch):
    legacy = _make_legacy(local_app_data)
    monkeypatch.setenv("ALFRED_DATABASE_PATH", "   ")

    assert config.resolve_database_path() == legacy


def test_the_legacy_path_is_still_reported_while_it_is_in_use(local_app_data):
    """`_default_database_path` stays pure: it reports, it does not move."""
    legacy = _make_legacy(local_app_data)

    assert config._default_database_path() == legacy
    assert legacy.exists()

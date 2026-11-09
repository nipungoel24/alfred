from functools import lru_cache
from pathlib import Path
import logging
import os
import sys
from pydantic import BaseModel, Field


def _load_dotenv_file(path: Path):
    """Best-effort dotenv load without extra dependencies."""
    try:
        if not path.exists():
            return
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    except Exception:
        pass


def _local_app_data() -> Path:
    return Path(os.getenv("LOCALAPPDATA", "."))


def _legacy_database_path() -> Path:
    """Where pre-AlfredData installs kept the mailbox.

    %LOCALAPPDATA%/Alfred also serves as the NSIS install directory, so the
    database used to sit beside the binaries an installer manages. See
    ADR-012.
    """
    return _local_app_data() / "Alfred" / "alfred.sqlite3"


def _managed_database_path() -> Path:
    """Where the mailbox belongs: a directory no installer owns."""
    return _local_app_data() / "AlfredData" / "alfred.sqlite3"


def _default_database_path() -> Path:
    """The database location, legacy installs included.

    Pure: it only reports where the file is. `migrate_legacy_user_data`
    does the moving, and `resolve_database_path` composes the two.
    """
    legacy = _legacy_database_path()
    if legacy.exists():
        return legacy
    return _managed_database_path()


#: Files that belong to the mailbox and must travel with it. The SQLite
#: sidecars are listed for completeness — migration refuses to run while
#: either exists, because their presence means unrecovered transactions.
_DATABASE_SIDECAR_SUFFIXES = ("-wal", "-shm")


def migrate_legacy_user_data() -> Path | None:
    """Move a legacy mailbox out of the install directory, or do nothing.

    Returns the directory data was moved into, or None if nothing moved.

    This is deliberately conservative: user data is never copied, never
    partially moved, and never deleted. Every refusal leaves the legacy
    layout exactly as it was, and the app keeps working from it, so a
    failure here costs the user nothing but a log line.

    It declines to act when:

    - there is no legacy database;
    - a managed database already exists (ambiguous — whichever is live is
      the caller's business, not a migration's);
    - a `-wal` or `-shm` file is present, meaning the last process did not
      close the database cleanly. Renaming a database away from its WAL
      loses committed transactions, so recovery data is left untouched and
      the next clean start migrates instead;
    - the rename fails for any reason, including a cross-volume move.
    """
    log = logging.getLogger("alfred.storage")

    # Belt and braces with the single call site in backend/sidecar.py: an
    # explicit database path means this process is pointed at its own file —
    # a test, a benchmark, a scratch verification run — and must not move the
    # real mailbox. backend/tests/conftest.py sets it for the whole suite.
    if os.getenv("ALFRED_DATABASE_PATH", "").strip():
        log.info("legacy_migration_skipped reason=explicit_database_path")
        return None

    legacy = _legacy_database_path()
    managed = _managed_database_path()

    if not legacy.exists():
        return None
    if managed.exists():
        log.warning(
            "legacy_migration_skipped reason=both_present legacy=%s managed=%s",
            legacy, managed,
        )
        return None

    unclean = [
        legacy.with_name(legacy.name + suffix)
        for suffix in _DATABASE_SIDECAR_SUFFIXES
        if legacy.with_name(legacy.name + suffix).exists()
    ]
    if unclean:
        log.warning(
            "legacy_migration_skipped reason=unclean_shutdown present=%s",
            ",".join(p.name for p in unclean),
        )
        return None

    # The mailbox and the user's own backups of it. Ollama's model store is
    # NOT Alfred's data and is never touched here.
    movable = [legacy] + sorted(legacy.parent.glob(legacy.name + "*.bak"))

    try:
        managed.parent.mkdir(parents=True, exist_ok=True)
        for source in movable:
            os.replace(source, managed.parent / source.name)
    except OSError as exc:
        log.warning(
            "legacy_migration_failed error=%s moved_so_far=%s keeping=%s",
            type(exc).__name__,
            sum(1 for p in movable if not p.exists()),
            legacy.parent,
        )
        return None

    log.info(
        "legacy_migration_complete files=%s from=%s to=%s",
        len(movable), legacy.parent, managed.parent,
    )
    return managed.parent


def resolve_database_path() -> Path:
    """The database path to use. Reports; never moves anything.

    Migration is deliberately NOT called from here. `backend.app.main` binds
    a Repository to this value at import time, and two test fixtures reload
    that module with the ALFRED_DATABASE_PATH guard removed — so anything
    reachable from this function runs against the user's real mailbox during
    `pytest`. Migration therefore has exactly one call site, in
    `backend/sidecar.py`, which only the packaged app executes.

    The override is short-circuited rather than passed as `os.getenv`'s
    default, so the default is not computed when it is not wanted.
    """
    override = os.getenv("ALFRED_DATABASE_PATH", "").strip()
    if override:
        return Path(override)
    return _default_database_path()


def _load_environment():
    """Loads configuration for dev or frozen production.

    Production (PyInstaller): the release builder embeds `production.env`
    inside the executable (--add-data) and may also place it next to the
    executable — the source tree and backend/.env are NOT required.
    Dev: backend/.env as before.
    """
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).parent
        candidates = [
            Path(getattr(sys, "_MEIPASS", "")) / "production.env",
            exe_dir / "production.env",
            exe_dir / "resources" / "production.env",
        ]
        for candidate in candidates:
            if candidate.exists():
                _load_dotenv_file(candidate)
                break
    else:
        env_path = Path(__file__).parent.parent / ".env"
        _load_dotenv_file(env_path)


def _reject_shipped_client_secret() -> None:
    """A frozen Alfred must not be carrying a Google OAuth client secret.

    Alfred authenticates as a Google **Desktop app** client using PKCE, for
    which Google's documentation lists ``client_secret`` as optional. A
    packaged build therefore has no legitimate use for one, and shipping it
    would distribute a credential to every user for no benefit.

    Failing loudly here means a mis-built artifact is caught at first launch
    rather than discovered later by a user.
    """
    if not getattr(sys, "frozen", False):
        return
    secret = os.getenv("GMAIL_CLIENT_SECRET", "").strip()
    if secret:
        raise RuntimeError(
            "This packaged build contains GMAIL_CLIENT_SECRET. Alfred uses a "
            "Google Desktop app client with PKCE and must not ship a client "
            "secret. Remove it from the build environment and rebuild with "
            "backend/build_sidecar.py. See docs/decisions/ADR-010."
        )


_load_environment()
_reject_shipped_client_secret()


class Settings(BaseModel):
    ollama_base_url: str = Field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"))
    ollama_model: str = Field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "qwen3:4b"))
    host: str = Field(default_factory=lambda: os.getenv("ALFRED_HOST", "127.0.0.1"))
    port: int = Field(default_factory=lambda: int(os.getenv("ALFRED_PORT", "8765")))
    database_path: Path = Field(default_factory=resolve_database_path)
    gmail_client_id: str = Field(default_factory=lambda: os.getenv("GMAIL_CLIENT_ID", "PLACEHOLDER_CLIENT_ID"))
    gmail_client_secret: str = Field(default_factory=lambda: os.getenv("GMAIL_CLIENT_SECRET", ""))
    # Build identity: passed by the Tauri shell (its own compile-time git
    # commit) when spawning the sidecar — proves which build is running.
    backend_build: str | None = Field(default_factory=lambda: os.getenv("ALFRED_BACKEND_BUILD") or None)
    # Desktop session auth: when set, every request must carry this token.
    # Generated per launch by the Tauri shell; never persisted.
    runtime_token: str | None = Field(default_factory=lambda: os.getenv("ALFRED_RUNTIME_TOKEN") or None)


@lru_cache
def get_settings() -> Settings:
    return Settings()

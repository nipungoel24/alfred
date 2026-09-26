from functools import lru_cache
from pathlib import Path
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


def _default_database_path() -> Path:
    """AppData database location.

    Legacy installs keep their data at %LOCALAPPDATA%/Alfred/alfred.sqlite3
    (the directory also served as the app install dir). New installs use
    %LOCALAPPDATA%/AlfredData/ so user data can never collide with — or be
    swept by — the application install directory.
    """
    legacy = Path(os.getenv("LOCALAPPDATA", ".")) / "Alfred" / "alfred.sqlite3"
    if legacy.exists():
        return legacy
    return Path(os.getenv("LOCALAPPDATA", ".")) / "AlfredData" / "alfred.sqlite3"


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
    database_path: Path = Field(default_factory=lambda: Path(os.getenv("ALFRED_DATABASE_PATH", _default_database_path())))
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

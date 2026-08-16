from functools import lru_cache
from pathlib import Path
import os
from pydantic import BaseModel, Field

# Load .env explicitly to ensure credentials are read reliably
try:
    from dotenv import load_dotenv
    # Look for .env in the current directory or its parents
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass


class Settings(BaseModel):
    ollama_base_url: str = Field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"))
    ollama_model: str = Field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "qwen3:4b"))
    host: str = Field(default_factory=lambda: os.getenv("ALFRED_HOST", "127.0.0.1"))
    port: int = Field(default_factory=lambda: int(os.getenv("ALFRED_PORT", "8765")))
    database_path: Path = Field(default_factory=lambda: Path(os.getenv("ALFRED_DATABASE_PATH", Path(os.getenv("LOCALAPPDATA", ".")) / "Alfred" / "alfred.sqlite3")))
    gmail_client_id: str = Field(default_factory=lambda: os.getenv("GMAIL_CLIENT_ID", "PLACEHOLDER_CLIENT_ID"))
    gmail_client_secret: str = Field(default_factory=lambda: os.getenv("GMAIL_CLIENT_SECRET", "PLACEHOLDER_CLIENT_SECRET"))


@lru_cache
def get_settings() -> Settings:
    return Settings()

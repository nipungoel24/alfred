from functools import lru_cache
from pathlib import Path
import os
from pydantic import BaseModel, Field


class Settings(BaseModel):
    ollama_base_url: str = Field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"))
    ollama_model: str = Field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "qwen3:4b"))
    host: str = Field(default_factory=lambda: os.getenv("ALFRED_HOST", "127.0.0.1"))
    port: int = Field(default_factory=lambda: int(os.getenv("ALFRED_PORT", "8765")))
    database_path: Path = Field(default_factory=lambda: Path(os.getenv("ALFRED_DATABASE_PATH", Path(os.getenv("LOCALAPPDATA", ".")) / "Alfred" / "alfred.sqlite3")))


@lru_cache
def get_settings() -> Settings:
    return Settings()

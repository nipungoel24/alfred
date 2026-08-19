"""Entrypoint packaged with PyInstaller for the Alfred desktop sidecar."""
import os
import sys

# Windowed PyInstaller builds have no console: sys.stdout/stderr are None,
# which breaks logging/uvicorn. Route them to devnull so the server can
# run fully headless (Tauri owns diagnostics via process events).
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")

import logging
import logging.handlers
from pathlib import Path


def _log_dir() -> Path:
    return Path(os.environ.get("LOCALAPPDATA", ".")) / "AlfredData" / "logs"


def _setup_file_logging():
    """Safe startup log: configuration booleans and failure categories.

    NEVER logs the runtime token, OAuth values, email bodies, or any
    other secret. Fields are timestamps, paths, and statuses only.
    """
    try:
        log_dir = _log_dir()
        log_dir.mkdir(parents=True, exist_ok=True)
        handler = logging.handlers.RotatingFileHandler(
            log_dir / "backend.log", maxBytes=1_000_000, backupCount=2,
            encoding="utf-8",
        )
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s"))
        root = logging.getLogger()
        root.addHandler(handler)
        root.setLevel(logging.INFO)
        return log_dir
    except Exception:
        return None


import uvicorn
from backend.app.config import get_settings
from backend.app.main import app

settings = get_settings()
log_dir = _setup_file_logging()

startup = logging.getLogger("alfred.startup")
startup.info(
    "sidecar_start port=%s db_path=%s frozen=%s config_present=%s token_set=%s",
    settings.port, settings.database_path, getattr(sys, "frozen", False),
    bool(settings.gmail_client_id and settings.gmail_client_id != "PLACEHOLDER_CLIENT_ID"),
    bool(settings.runtime_token),
)
if log_dir:
    startup.info("log_dir=%s", log_dir)

config = uvicorn.Config(app, host="127.0.0.1", port=settings.port, log_level="info")
server = uvicorn.Server(config)
try:
    server.run()
except Exception as exc:  # noqa: BLE001 — crash diagnostics, never silent
    logging.getLogger("alfred.startup").exception(
        "sidecar_crashed category=%s", type(exc).__name__)
    raise

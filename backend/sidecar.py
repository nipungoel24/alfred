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

import uvicorn
from backend.app.config import get_settings
from backend.app.main import app

settings = get_settings()
config = uvicorn.Config(app, host="127.0.0.1", port=settings.port, log_level="warning")
server = uvicorn.Server(config)
server.run()

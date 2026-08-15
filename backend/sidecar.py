"""Entrypoint packaged with PyInstaller for the Alfred desktop sidecar."""
import uvicorn
from backend.app.config import get_settings
from backend.app.main import app

settings = get_settings()
config = uvicorn.Config(app, host="127.0.0.1", port=settings.port, log_level="warning")
server = uvicorn.Server(config)
server.run()

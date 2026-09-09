"""Session guard: backend tests must never touch the user's live database.

Importing backend.app.main binds a Repository to ALFRED_DATABASE_PATH at
import time. Redirect that default to a session-scoped scratch directory
before any test module is imported. Individual tests keep using tmp_path
fixtures and explicit monkeypatched paths (which override this); this is
only the safety default for the import-time binding.
"""
import os
import tempfile
from pathlib import Path

_session_dir = Path(tempfile.mkdtemp(prefix="alfred_pytest_session_"))
os.environ.setdefault(
    "ALFRED_DATABASE_PATH", str(_session_dir / "session.sqlite3")
)

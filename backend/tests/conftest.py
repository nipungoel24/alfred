"""Session guard: backend tests must never touch the user's live database.

Importing backend.app.main binds a Repository to ALFRED_DATABASE_PATH at
import time. Redirect that default to a session-scoped scratch directory
before any test module is imported. Individual tests keep using tmp_path
fixtures and explicit monkeypatched paths (which override this); this is
only the safety default for the import-time binding.

A fixture that needs its own database must point the variable at one. It
must NEVER unset it and then reload backend.app.main: that binds a
Repository to %LOCALAPPDATA%, which is the user's live mailbox. Two
fixtures did exactly that until 2026-11-09, and
test_no_fixture_unsets_the_live_mailbox_guard now forbids it. Use
SESSION_DATABASE below to restore the default instead.
"""
import os
import tempfile
from pathlib import Path

_session_dir = Path(tempfile.mkdtemp(prefix="alfred_pytest_session_"))

#: The scratch database every test falls back to. Fixtures that temporarily
#: redirect ALFRED_DATABASE_PATH restore it to this, never to "unset".
SESSION_DATABASE = _session_dir / "session.sqlite3"

os.environ.setdefault("ALFRED_DATABASE_PATH", str(SESSION_DATABASE))

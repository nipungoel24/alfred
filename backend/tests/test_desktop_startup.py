"""Desktop startup regression tests.

Covers the installed-startup failure classes:
- /health must serve IMMEDIATELY, not hang behind slow lifespan work
  (model preload / task rebuild / backfill resume).
- OAuth callback remains exempt from the runtime token.
"""
import asyncio
import os
import time

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def startup_app(tmp_path, monkeypatch):
    monkeypatch.setenv("ALFRED_RUNTIME_TOKEN", "startup-test-token")
    monkeypatch.setenv("ALFRED_DATABASE_PATH", str(tmp_path / "startup.db"))
    import importlib
    from backend.app import config as config_mod
    from backend.app import main as main_mod
    importlib.reload(config_mod)
    importlib.reload(main_mod)
    yield main_mod
    monkeypatch.delenv("ALFRED_RUNTIME_TOKEN")
    monkeypatch.delenv("ALFRED_DATABASE_PATH")
    importlib.reload(config_mod)
    importlib.reload(main_mod)


def test_health_serves_without_waiting_for_slow_startup(startup_app, monkeypatch):
    """The desktop shell probes /health on a bounded timeout.

    If the lifespan awaits slow work (e.g. Ollama model preload) before
    yielding, health hangs and the shell reports BACKEND_TIMEOUT. Health
    must answer as soon as the socket is up; slow work belongs in
    background tasks.
    """
    main = startup_app
    release = asyncio.Event()

    async def slow_preload():
        release.set()          # prove the background task started
        await asyncio.sleep(8)  # simulate a very slow Ollama load
        raise RuntimeError("unreachable in test")

    monkeypatch.setattr(main.ai, "preload", slow_preload)

    with TestClient(main.app) as client:
        t0 = time.perf_counter()
        r = client.get("/health", headers={"X-Alfred-Token": "startup-test-token"})
        elapsed = time.perf_counter() - t0
        assert r.status_code == 200
        # Health answered essentially immediately (startup didn't block)
        assert elapsed < 3.0, f"health took {elapsed:.1f}s — lifespan is blocking"
        # The slow startup work really was scheduled in the background
        assert release.is_set()


def test_oauth_callback_exempt_under_token(startup_app):
    main = startup_app
    with TestClient(main.app) as client:
        r = client.get("/api/accounts/gmail/callback",
                       params={"code": "x", "state": "bogus"})
        assert r.status_code == 400
        assert "text/html" in r.headers.get("content-type", "")

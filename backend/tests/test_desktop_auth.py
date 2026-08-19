"""Desktop session-auth middleware + graceful shutdown tests."""
import json
import os
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def authed_app(tmp_path, monkeypatch):
    monkeypatch.setenv("ALFRED_RUNTIME_TOKEN", "test-secret-token-123")
    monkeypatch.setenv("ALFRED_DATABASE_PATH", str(tmp_path / "auth.db"))
    # Reload settings + app under the modified env
    import importlib
    from backend.app import config as config_mod
    from backend.app import main as main_mod
    importlib.reload(config_mod)
    importlib.reload(main_mod)
    yield main_mod.app, main_mod
    # Restore defaults for other tests
    monkeypatch.delenv("ALFRED_RUNTIME_TOKEN")
    monkeypatch.delenv("ALFRED_DATABASE_PATH")
    importlib.reload(config_mod)
    importlib.reload(main_mod)


def test_api_requires_token(authed_app):
    app, _ = authed_app
    client = TestClient(app)
    # No token → 401 on API paths
    r = client.get("/api/accounts")
    assert r.status_code == 401
    # Wrong token → 401
    r = client.get("/api/accounts", headers={"X-Alfred-Token": "wrong"})
    assert r.status_code == 401
    # Correct header → 200
    r = client.get("/api/accounts", headers={"X-Alfred-Token": "test-secret-token-123"})
    assert r.status_code == 200


def test_health_requires_token_when_enabled(authed_app):
    app, _ = authed_app
    client = TestClient(app)
    assert client.get("/health").status_code == 401
    r = client.get("/health", headers={"X-Alfred-Token": "test-secret-token-123"})
    assert r.status_code == 200


def test_query_token_form_for_sse(authed_app):
    app, _ = authed_app
    client = TestClient(app)
    r = client.get("/api/analysis/status?token=test-secret-token-123")
    assert r.status_code == 200


def test_shutdown_endpoint_is_token_protected(authed_app):
    app, _ = authed_app
    client = TestClient(app)
    assert client.post("/api/shutdown").status_code == 401


def test_no_token_means_no_auth(tmp_path, monkeypatch):
    """Dev mode: without ALFRED_RUNTIME_TOKEN the API stays open."""
    monkeypatch.setenv("ALFRED_DATABASE_PATH", str(tmp_path / "dev.db"))
    import importlib
    from backend.app import config as config_mod
    from backend.app import main as main_mod
    importlib.reload(config_mod)
    importlib.reload(main_mod)
    try:
        client = TestClient(main_mod.app)
        assert client.get("/api/accounts").status_code == 200
        assert client.get("/health").status_code == 200
    finally:
        monkeypatch.delenv("ALFRED_DATABASE_PATH")
        importlib.reload(config_mod)
        importlib.reload(main_mod)

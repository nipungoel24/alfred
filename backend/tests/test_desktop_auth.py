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


def test_oauth_callback_is_exempt_from_token(authed_app):
    """The system browser's OAuth redirect carries no session token — its
    security is the one-time PKCE state. The middleware must not 401 it."""
    app, _ = authed_app
    client = TestClient(app)
    # Unknown state → the handler itself must answer (styled failure page),
    # NOT the token middleware.
    r = client.get("/api/accounts/gmail/callback", params={"code": "x", "state": "bogus"})
    assert r.status_code == 400
    assert "text/html" in r.headers.get("content-type", "")
    assert "UNAUTHORIZED" not in r.text


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


def test_cors_preflight_passes_without_token(authed_app):
    """Browsers never attach the session token to CORS preflights.

    Regression: the packaged Windows WebView (origin http://tauri.localhost)
    sends OPTIONS preflights for every fetch carrying X-Alfred-Token. The
    token middleware must not 401 them or the frontend gets zero data.
    """
    app, _ = authed_app
    client = TestClient(app)
    r = client.options(
        "/api/emails/counts",
        headers={
            "Origin": "http://tauri.localhost",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "x-alfred-token",
        },
    )
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == "http://tauri.localhost"
    assert "x-alfred-token" in r.headers.get("access-control-allow-headers", "")


def test_windows_tauri_origin_gets_cors_headers(authed_app):
    """Actual requests from the packaged Windows WebView must carry the
    ACAO header or the browser drops the response silently."""
    app, _ = authed_app
    client = TestClient(app)
    r = client.get(
        "/api/emails/counts",
        headers={"Origin": "http://tauri.localhost", "X-Alfred-Token": "test-secret-token-123"},
    )
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == "http://tauri.localhost"


def test_unix_tauri_origin_still_supported(authed_app):
    app, _ = authed_app
    client = TestClient(app)
    r = client.get(
        "/api/emails/counts",
        headers={"Origin": "tauri://localhost", "X-Alfred-Token": "test-secret-token-123"},
    )
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == "tauri://localhost"


def test_unknown_origin_gets_no_cors_headers(authed_app):
    """CORS stays restrictive: unlisted origins must not receive ACAO."""
    app, _ = authed_app
    client = TestClient(app)
    r = client.get(
        "/api/emails/counts",
        headers={"Origin": "http://evil.example.com", "X-Alfred-Token": "test-secret-token-123"},
    )
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") is None


def test_preflight_exemption_does_not_open_actual_requests(authed_app):
    """Passing OPTIONS through must not weaken token enforcement on GET."""
    app, _ = authed_app
    client = TestClient(app)
    preflight = client.options(
        "/api/emails/counts",
        headers={
            "Origin": "http://tauri.localhost",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "x-alfred-token",
        },
    )
    assert preflight.status_code == 200
    assert client.get("/api/emails/counts").status_code == 401

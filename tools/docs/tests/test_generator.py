"""Tests for the Alfred knowledge-graph generator."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent.parent
GEN = ROOT / "tools" / "docs" / "generate_knowledge_graph.py"
VAULT_GEN = ROOT / "docs" / "obsidian" / "99 - Generated"


@pytest.fixture(scope="session")
def graph_data():
    # Run the FULL generator once (keeps the committed generated docs
    # complete, including TypeScript notes).
    res = subprocess.run([sys.executable, str(GEN)],
                         capture_output=True, text=True, timeout=900)
    assert res.returncode == 0, res.stderr[-1000:]
    index = json.loads((VAULT_GEN / "repository-index.json").read_text(encoding="utf-8"))
    dep = json.loads((VAULT_GEN / "dependency-graph.json").read_text(encoding="utf-8"))
    return index, dep


def test_repository_index_shape(graph_data):
    index, _ = graph_data
    for key in ("languages", "modules", "classes", "functions", "api_endpoints",
                "database_tables", "tests"):
        assert key in index, key


def test_key_symbols_present(graph_data):
    index, _ = graph_data
    symbols = index["classes"] + index["functions"]
    for q in ("backend.app.ai.service.AIService",
              "backend.app.mail.providers.gmail.GmailProvider",
              "backend.app.db.repositories.Repository",
              "backend.app.services.task_derivation.derive_tasks",
              "backend.app.main.sync_account"):
        assert q in symbols, q


def test_fastapi_routes_detected(graph_data):
    index, _ = graph_data
    eps = index["api_endpoints"]
    assert any("POST /api/accounts/{account_id}/sync" in e or
               "POST -api-accounts-{account_id}-sync" in e for e in eps)
    assert any("/api/emails" in e for e in eps)
    assert any("/api/briefing" in e for e in eps)


def test_database_tables_detected(graph_data):
    index, _ = graph_data
    for t in ("accounts", "credentials", "emails", "email_analysis", "tasks",
              "jobs", "inbox_briefing", "inference_metrics"):
        assert t in index["database_tables"], t


def test_reverse_call_links(graph_data):
    _, dep = graph_data
    nodes = {n["id"] for n in dep["nodes"]}
    # derive_tasks is called by the worker and migration service
    callees = [e for e in dep["edges"]
               if e["to"] == "backend.app.services.task_derivation.derive_tasks"]
    assert len(callees) >= 1
    # every resolved edge's endpoints are known nodes
    for e in dep["edges"]:
        assert e["from"] in nodes
        assert e["to"] in nodes


def test_generated_marker():
    sample = VAULT_GEN / "Functions" / "backend.app.ai.service.AIService.analyze_email.md"
    assert sample.exists()
    text = sample.read_text(encoding="utf-8")
    assert "Auto-generated from source code" in text
    assert "qualified_name: backend.app.ai.service.AIService.analyze_email" in text


def test_no_absolute_machine_paths(graph_data):
    index, _ = graph_data
    assert "C:\\" not in json.dumps(index)
    assert "C:/" not in json.dumps(index)
    assert "Users\\" not in json.dumps(index)


def test_check_mode_current():
    res = subprocess.run([sys.executable, str(GEN), "--check"],
                         capture_output=True, text=True, timeout=600)
    assert res.returncode == 0, res.stdout[-500:] + res.stderr[-500:]


def test_check_mode_detects_staleness(tmp_path):
    # Simulate drift by touching a generated file, then restore.
    target = VAULT_GEN / "repository-index.json"
    original = target.read_text(encoding="utf-8")
    try:
        target.write_text(original.replace("languages", "languagesXX"), encoding="utf-8")
        res = subprocess.run([sys.executable, str(GEN), "--check"],
                             capture_output=True, text=True, timeout=600)
        assert res.returncode != 0
    finally:
        target.write_text(original, encoding="utf-8")

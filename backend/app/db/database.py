"""SQLite schema and connection helpers for Alfred's local data."""
import sqlite3
from pathlib import Path

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS emails (id TEXT PRIMARY KEY, payload TEXT NOT NULL, content_hash TEXT NOT NULL, imported_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS email_analysis (email_id TEXT PRIMARY KEY, content_hash TEXT NOT NULL, model_name TEXT NOT NULL, schema_version TEXT NOT NULL, payload TEXT NOT NULL, analyzed_at TEXT NOT NULL, FOREIGN KEY(email_id) REFERENCES emails(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS inbox_briefing (fingerprint TEXT PRIMARY KEY, model_name TEXT NOT NULL, schema_version TEXT NOT NULL, payload TEXT NOT NULL, generated_at TEXT NOT NULL);
"""

def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    return connection

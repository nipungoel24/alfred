"""SQLite schema and connection helpers for Alfred's local data."""
import sqlite3
from pathlib import Path

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS emails (
    id TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    imported_at TEXT NOT NULL,
    account_id TEXT,
    thread_id TEXT
);
CREATE TABLE IF NOT EXISTS email_analysis (
    email_id TEXT PRIMARY KEY,
    content_hash TEXT NOT NULL,
    model_name TEXT NOT NULL,
    schema_version TEXT NOT NULL,
    payload TEXT NOT NULL,
    analyzed_at TEXT NOT NULL,
    FOREIGN KEY(email_id) REFERENCES emails(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS inbox_briefing (
    fingerprint TEXT PRIMARY KEY,
    model_name TEXT NOT NULL,
    schema_version TEXT NOT NULL,
    payload TEXT NOT NULL,
    generated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS accounts (
    id TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    email_address TEXT NOT NULL,
    display_name TEXT,
    connection_status TEXT NOT NULL,
    last_sync_at TEXT,
    sync_cursor TEXT,
    created_at TEXT,
    updated_at TEXT
);
CREATE TABLE IF NOT EXISTS credentials (
    account_id TEXT PRIMARY KEY REFERENCES accounts(id) ON DELETE CASCADE,
    encrypted_refresh_token BLOB,
    encrypted_access_token BLOB,
    expires_at TEXT
);
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    source_email_id TEXT REFERENCES emails(id) ON DELETE SET NULL,
    source_thread_id TEXT,
    title TEXT NOT NULL,
    description TEXT,
    due_at TEXT,
    priority TEXT,
    status TEXT NOT NULL,
    created_at TEXT
);
"""

def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    
    # Run simple migrations for legacy databases
    cursor = connection.cursor()
    cursor.execute("PRAGMA table_info(emails)")
    columns = [row["name"] for row in cursor.fetchall()]
    if "account_id" not in columns:
        cursor.execute("ALTER TABLE emails ADD COLUMN account_id TEXT")
    if "thread_id" not in columns:
        cursor.execute("ALTER TABLE emails ADD COLUMN thread_id TEXT")
    connection.commit()
    return connection


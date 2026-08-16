"""SQLite schema, connection, and migration helpers for Alfred's local data."""
import sqlite3
from pathlib import Path
from contextlib import contextmanager

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS emails (
    id TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    imported_at TEXT NOT NULL,
    account_id TEXT,
    thread_id TEXT,
    sender_col TEXT,
    subject_col TEXT,
    received_at_col TEXT
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
    created_at TEXT,
    derivation_version TEXT DEFAULT '1',
    confidence TEXT DEFAULT 'medium',
    fingerprint TEXT
);
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    job_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    priority INTEGER DEFAULT 50,
    status TEXT NOT NULL DEFAULT 'queued',
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 2,
    created_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    error_code TEXT,
    error_message TEXT
);
CREATE TABLE IF NOT EXISTS inference_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT,
    model TEXT NOT NULL,
    total_ms REAL,
    load_ms REAL,
    prompt_eval_ms REAL,
    eval_ms REAL,
    prompt_tokens INTEGER,
    output_tokens INTEGER,
    cache_hit INTEGER DEFAULT 0,
    success INTEGER DEFAULT 1,
    recorded_at TEXT NOT NULL
);
"""

INDEXES = """
CREATE INDEX IF NOT EXISTS idx_emails_account_imported ON emails(account_id, imported_at DESC);
CREATE INDEX IF NOT EXISTS idx_emails_thread ON emails(thread_id);
CREATE INDEX IF NOT EXISTS idx_emails_received ON emails(received_at_col DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_email ON email_analysis(email_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_source ON tasks(source_email_id);
CREATE INDEX IF NOT EXISTS idx_tasks_thread ON tasks(source_thread_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status_priority ON jobs(status, priority DESC, created_at ASC);
"""

# FTS5 virtual table for full-text search
FTS_SCHEMA = """
CREATE VIRTUAL TABLE IF NOT EXISTS emails_fts USING fts5(
    subject,
    sender,
    body,
    content='',
    tokenize='unicode61'
);
"""


def connect(path: Path) -> sqlite3.Connection:
    """Create an optimized SQLite connection with WAL mode and indexes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, check_same_thread=False)
    connection.row_factory = sqlite3.Row

    # Performance PRAGMAs — applied before schema creation
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA synchronous=NORMAL")
    connection.execute("PRAGMA busy_timeout=5000")
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("PRAGMA cache_size=-8000")  # 8MB page cache

    # Create tables
    connection.executescript(SCHEMA)

    # Run migrations for legacy databases
    _migrate(connection)

    # Create indexes (idempotent)
    connection.executescript(INDEXES)

    # Create FTS5 table (idempotent)
    try:
        connection.executescript(FTS_SCHEMA)
    except sqlite3.OperationalError:
        pass  # FTS5 may not be available in all SQLite builds

    # Optimize query planner statistics
    connection.execute("PRAGMA optimize")
    connection.commit()

    return connection


def _migrate(connection: sqlite3.Connection):
    """Run incremental schema migrations for legacy databases."""
    cursor = connection.cursor()

    # emails table migrations
    cursor.execute("PRAGMA table_info(emails)")
    email_cols = {row["name"] for row in cursor.fetchall()}
    for col, col_type in [("account_id", "TEXT"), ("thread_id", "TEXT"),
                          ("sender_col", "TEXT"), ("subject_col", "TEXT"),
                          ("received_at_col", "TEXT")]:
        if col not in email_cols:
            cursor.execute(f"ALTER TABLE emails ADD COLUMN {col} {col_type}")

    # tasks table migrations
    cursor.execute("PRAGMA table_info(tasks)")
    task_cols = {row["name"] for row in cursor.fetchall()}
    for col, col_type in [("derivation_version", "TEXT DEFAULT '1'"),
                          ("confidence", "TEXT DEFAULT 'medium'"),
                          ("fingerprint", "TEXT")]:
        col_name = col.split()[0]  # Handle "derivation_version TEXT DEFAULT '1'" -> "derivation_version"
        if col_name not in task_cols:
            cursor.execute(f"ALTER TABLE tasks ADD COLUMN {col}")

    connection.commit()


@contextmanager
def transaction(connection: sqlite3.Connection):
    """Context manager for batched write transactions.
    
    Usage:
        with transaction(con) as cur:
            cur.execute(...)
            cur.execute(...)
        # commit happens automatically on exit
    """
    cursor = connection.cursor()
    cursor.execute("BEGIN IMMEDIATE")
    try:
        yield cursor
        connection.commit()
    except Exception:
        connection.rollback()
        raise

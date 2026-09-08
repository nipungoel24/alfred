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
    received_at_col TEXT,
    label_ids_json TEXT,
    mailbox_state TEXT,
    gmail_category TEXT,
    pipeline_eligibility TEXT
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
    error_message TEXT,
    not_before TEXT
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
CREATE INDEX IF NOT EXISTS idx_emails_state_category ON emails(account_id, mailbox_state, gmail_category, received_at_col DESC);
CREATE INDEX IF NOT EXISTS idx_emails_state_received ON emails(mailbox_state, received_at_col DESC);
CREATE INDEX IF NOT EXISTS idx_emails_eligibility ON emails(pipeline_eligibility);
CREATE INDEX IF NOT EXISTS idx_analysis_email ON email_analysis(email_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_source ON tasks(source_email_id);
CREATE INDEX IF NOT EXISTS idx_tasks_thread ON tasks(source_thread_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status_priority ON jobs(status, priority DESC, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_jobs_status_notbefore ON jobs(status, not_before);
"""

# FTS5 virtual table for full-text search — contentless-delete=1 allows
# individual row deletions while keeping the storage-efficient contentless
# design. Requires SQLite >= 3.43.0 (shipped with Python 3.12+).
FTS_SCHEMA = """
CREATE VIRTUAL TABLE IF NOT EXISTS emails_fts USING fts5(
    subject,
    sender,
    body,
    content='',
    contentless_delete=1,
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
                          ("received_at_col", "TEXT"),
                          ("label_ids_json", "TEXT"),
                          ("mailbox_state", "TEXT"),
                          ("gmail_category", "TEXT"),
                          ("pipeline_eligibility", "TEXT")]:
        if col not in email_cols:
            cursor.execute(f"ALTER TABLE emails ADD COLUMN {col} {col_type}")

    # Backfill mailbox state / category / eligibility from stored payloads
    # when the new columns are empty but Gmail raw metadata is present.
    try:
        from ..mail.eligibility import (
            MailEligibilityPolicy, gmail_category_from_labels,
            mailbox_state_from_labels,
        )
        rows = cursor.execute(
            "SELECT id, payload, label_ids_json FROM emails WHERE label_ids_json IS NULL"
        ).fetchall()
        if rows:
            import json as _json
            for r in rows:
                label_ids = None
                try:
                    payload = _json.loads(r["payload"])
                    raw = payload.get("source_metadata", {}).get("gmail_raw", {})
                    stored = raw.get("labelIds")
                    if isinstance(stored, list):
                        label_ids = [str(l) for l in stored]
                except Exception:
                    pass
                if not label_ids:
                    continue
                state = mailbox_state_from_labels(label_ids)
                category = gmail_category_from_labels(label_ids)
                eligibility = MailEligibilityPolicy.pipeline_eligibility(label_ids)
                # Also patch the label_ids inside the payload JSON so
                # runtime reads of Email.label_ids agree with the columns.
                try:
                    payload["label_ids"] = label_ids
                    new_payload = _json.dumps(payload)
                except Exception:
                    new_payload = r["payload"]
                cursor.execute(
                    "UPDATE emails SET label_ids_json=?, mailbox_state=?, gmail_category=?, "
                    "pipeline_eligibility=?, payload=? WHERE id=?",
                    (_json.dumps(label_ids), state.value, category.value, eligibility.value,
                     new_payload, r["id"])
                )
    except Exception:
        pass  # Non-fatal: runtime backfill can also refresh via Gmail metadata

    # Repair pass: rows whose columns were backfilled by an earlier run but
    # whose payload JSON still carries an empty label_ids list. Keeps
    # runtime Email.label_ids reads consistent with the persisted columns.
    try:
        import json as _json
        rows = cursor.execute(
            "SELECT id, payload, label_ids_json FROM emails "
            "WHERE label_ids_json IS NOT NULL AND label_ids_json != '[]'"
        ).fetchall()
        patched = 0
        for r in rows:
            try:
                payload = _json.loads(r["payload"])
                if payload.get("label_ids"):
                    continue
                payload["label_ids"] = _json.loads(r["label_ids_json"])
                cursor.execute(
                    "UPDATE emails SET payload=? WHERE id=?",
                    (_json.dumps(payload), r["id"])
                )
                patched += 1
            except Exception:
                continue
        if patched:
            print(f"[Alfred] Repaired label_ids in {patched} cached email payloads")
    except Exception:
        pass
    connection.commit()

    # Item 4: Migrate raw Gmail IDs to account-prefixed scoped IDs.
    # Before this migration, emails.id stored the raw Gmail message ID.
    # Now _normalize_message() generates "gmail_{account_id}_{raw_msg_id}".
    # This migration is idempotent: already-scoped IDs are skipped.
    try:
        import json as _json
        import re
        _scoped_re = re.compile(r'^gmail_[^_]+_.+')
        rows = cursor.execute(
            "SELECT id, account_id, payload FROM emails WHERE id NOT LIKE 'gmail_%' OR id NOT LIKE 'gmail_%_%'"
        ).fetchall()
        migrated = 0
        for r in rows:
            raw_id = r["id"]
            account_id = r["account_id"]
            if not account_id or _scoped_re.match(raw_id):
                continue  # Already scoped or missing account
            scoped_id = f"gmail_{account_id}_{raw_id}"
            # Check for collision (unlikely but safe)
            exists = cursor.execute("SELECT 1 FROM emails WHERE id=?", (scoped_id,)).fetchone()
            if exists:
                continue  # Scoped version already exists, skip
            # Update email_analysis FK
            cursor.execute(
                "UPDATE email_analysis SET email_id=? WHERE email_id=?",
                (scoped_id, raw_id)
            )
            # Update tasks FK
            cursor.execute(
                "UPDATE tasks SET source_email_id=? WHERE source_email_id=?",
                (scoped_id, raw_id)
            )
            # Update jobs FK (target_id references email_id)
            cursor.execute(
                "UPDATE jobs SET target_id=? WHERE target_id=? AND job_type IN ('analyze','backfill')",
                (scoped_id, raw_id)
            )
            # Update the emails table itself
            cursor.execute("UPDATE emails SET id=? WHERE id=?", (scoped_id, raw_id))
            migrated += 1
        if migrated:
            print(f"[Alfred] Migrated {migrated} email IDs to account-prefixed format")
            # Rebuild FTS after ID migration
            try:
                cursor.execute("DROP TABLE IF EXISTS emails_fts")
                cursor.executescript(FTS_SCHEMA)
            except Exception:
                pass
    except Exception:
        pass  # Non-fatal: new emails use scoped IDs automatically
    connection.commit()

    # tasks table migrations
    cursor.execute("PRAGMA table_info(tasks)")
    task_cols = {row["name"] for row in cursor.fetchall()}
    for col, col_type in [("derivation_version", "TEXT DEFAULT '1'"),
                          ("confidence", "TEXT DEFAULT 'medium'"),
                          ("fingerprint", "TEXT")]:
        col_name = col.split()[0]  # Handle "derivation_version TEXT DEFAULT '1'" -> "derivation_version"
        if col_name not in task_cols:
            cursor.execute(f"ALTER TABLE tasks ADD COLUMN {col}")

    # jobs table migrations (scheduled/backoff-aware queueing)
    cursor.execute("PRAGMA table_info(jobs)")
    job_cols = {row["name"] for row in cursor.fetchall()}
    for col, col_type in [("not_before", "TEXT")]:
        if col not in job_cols:
            cursor.execute(f"ALTER TABLE jobs ADD COLUMN {col} {col_type}")

    connection.commit()


@contextmanager
def transaction(connection: sqlite3.Connection):
    """Context manager for batched write transactions.

    Tolerates callers that already have an implicit transaction open
    (e.g. a bare INSERT without commit): a nested BEGIN would raise
    OperationalError, so only begin when no transaction is active.

    Usage:
        with transaction(con) as cur:
            cur.execute(...)
            cur.execute(...)
        # commit happens automatically on exit
    """
    cursor = connection.cursor()
    if not connection.in_transaction:
        cursor.execute("BEGIN IMMEDIATE")
    try:
        yield cursor
        connection.commit()
    except Exception:
        connection.rollback()
        raise

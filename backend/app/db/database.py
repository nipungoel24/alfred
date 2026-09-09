"""SQLite schema, connection, and migration helpers for Alfred's local data."""
import sqlite3
from pathlib import Path
from contextlib import contextmanager

# sqlite3.Connection does not allow attribute assignment and is not
# weak-referenceable; cache the per-connection FTS capability probe here
# (id-keyed; a redundant probe is harmless and idempotent).
_fts_delete_cache: dict[int, bool] = {}


class MigrationSafetyError(Exception):
    """Refusing to open the database for normal writes.

    Raised when a data migration cannot create its safety snapshot.
    Fail-closed: the repository/backend must NOT continue against an
    unmigrated database where sync could insert scoped duplicates beside
    legacy raw rows. The message carries only operational details (paths),
    never email content or credentials.
    """


def _sqlite_backup(source: sqlite3.Connection, backup_file: Path):
    """Write a consistent snapshot of `source` to `backup_file`.

    Uses the SQLite online-backup API, which is safe under WAL mode and
    includes committed WAL state. Raises on any failure — callers treat a
    failed backup as an aborted migration, never as a warning to skip.
    Only sanitized operational details (paths) are logged by callers.
    """
    backup_file.parent.mkdir(parents=True, exist_ok=True)
    target = sqlite3.connect(str(backup_file))
    try:
        with target:
            source.backup(target)
    finally:
        target.close()


def snapshot_database(source_path: Path, dest_path: Path):
    """WAL-safe snapshot of a database FILE to another path.

    Read-only against the source (the backup API never mutates it), so
    verification tooling can snapshot a live production database without
    touching it. Raises on failure.
    """
    source = sqlite3.connect(str(source_path))
    try:
        _sqlite_backup(source, dest_path)
    finally:
        source.close()

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
    pipeline_eligibility TEXT,
    provider_message_id TEXT
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

# Fallback for SQLite builds older than 3.43.0 (no contentless_delete):
# the index then requires full rebuilds after updates/deletes.
FTS_SCHEMA_LEGACY = """
CREATE VIRTUAL TABLE IF NOT EXISTS emails_fts USING fts5(
    subject,
    sender,
    body,
    content='',
    tokenize='unicode61'
);
"""


def fts_delete_supported(connection: sqlite3.Connection) -> bool:
    """Does the RUNTIME SQLite support contentless_delete=1?

    Probed with an isolated temporary table — never against the real
    production table name, so an already-existing legacy table can never
    produce a false positive. The packaged Windows runtime bundles its own
    SQLite; this is never assumed from the developer machine.
    """
    cached = _fts_delete_cache.get(id(connection))
    if cached is not None:
        return cached
    supported = True
    try:
        connection.execute("DROP TABLE IF EXISTS alfred_fts_cap_probe")
        connection.execute(
            "CREATE VIRTUAL TABLE alfred_fts_cap_probe USING fts5("
            "subject, sender, body, content='', contentless_delete=1, "
            "tokenize='unicode61')"
        )
        connection.execute("DROP TABLE alfred_fts_cap_probe")
    except sqlite3.OperationalError:
        supported = False
        try:
            connection.execute("DROP TABLE IF EXISTS alfred_fts_cap_probe")
        except sqlite3.OperationalError:
            pass
    _fts_delete_cache[id(connection)] = supported
    return supported


def fts_table_uses_contentless_delete(connection: sqlite3.Connection) -> bool | None:
    """What schema does the EXISTING emails_fts table actually use?

    Returns True/False, or None when no emails_fts table exists. Inspects
    the stored sqlite_master definition — never inferred from the runtime.
    """
    row = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='emails_fts'"
    ).fetchone()
    if not row or not row[0]:
        return None
    return "contentless_delete" in row[0]


def repopulate_fts_index(connection: sqlite3.Connection):
    """Re-index every email row into emails_fts (content repair)."""
    connection.execute(
        "INSERT INTO emails_fts(rowid, subject, sender, body) "
        "SELECT rowid, "
        "COALESCE(subject_col, json_extract(payload, '$.subject'), ''), "
        "COALESCE(sender_col, json_extract(payload, '$.sender'), ''), "
        "COALESCE(json_extract(payload, '$.body'), '') "
        "FROM emails"
    )


def ensure_fts_schema(connection: sqlite3.Connection):
    """Idempotent FTS schema + content guarantee, run on every connect().

    - No table: create the variant the runtime supports, then index.
    - Legacy table (no contentless_delete) on a capable runtime: migrate
      explicitly (drop, recreate, re-index).
    - Matching schema but empty index with non-empty mailbox: re-index
      (covers interrupted migrations; contentless tables report COUNT(*)
      over indexed rows).
    - Incapable runtime: legacy schema; per-row maintenance falls back to
      rebuilds in the repository layer.
    """
    import logging as _logging
    logger = _logging.getLogger("alfred.fts")
    try:
        capable = fts_delete_supported(connection)
    except Exception as exc:
        logger.warning("fts_capability_probe_failed: %s", exc)
        return
    existing = fts_table_uses_contentless_delete(connection)
    try:
        if existing is None:
            connection.execute(FTS_SCHEMA if capable else FTS_SCHEMA_LEGACY)
            repopulate_fts_index(connection)
            connection.commit()
        elif capable and not existing:
            logger.info("fts_schema_upgrade: legacy contentless table found; migrating")
            connection.execute("DROP TABLE emails_fts")
            connection.execute(FTS_SCHEMA)
            repopulate_fts_index(connection)
            connection.commit()
            logger.info("fts_schema_upgrade: complete")
        else:
            try:
                fts_rows = connection.execute(
                    "SELECT COUNT(*) FROM emails_fts").fetchone()[0]
                mail_rows = connection.execute(
                    "SELECT COUNT(*) FROM emails").fetchone()[0]
            except sqlite3.OperationalError:
                return  # FTS5 unavailable in this build
            if mail_rows and not fts_rows:
                repopulate_fts_index(connection)
                connection.commit()
    except sqlite3.OperationalError as exc:
        logger.warning("fts_ensure_failed: %s", exc)


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

    # Account-safe provider identity: one provider message belongs to one
    # account row. Partial index — legacy/CSV rows with NULLs stay exempt.
    # Created tolerantly: a legacy database with pre-existing duplicates
    # must never fail to open; the situation is logged instead.
    try:
        connection.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_emails_account_provider "
            "ON emails(account_id, provider_message_id) "
            "WHERE account_id IS NOT NULL AND provider_message_id IS NOT NULL"
        )
    except sqlite3.IntegrityError as exc:
        import logging as _logging
        _logging.getLogger("alfred.db").warning(
            "provider_unique_index_skipped: %s", exc)

    # FTS5 schema + content guarantee (idempotent; migrates legacy
    # contentless tables on capable runtimes, falls back otherwise).
    ensure_fts_schema(connection)

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
                          ("pipeline_eligibility", "TEXT"),
                          ("provider_message_id", "TEXT")]:
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
    #
    # Safety properties (idempotent, lossless):
    # - a backup copy of the database is made before the first rename
    # - already-scoped rows are detected by parsing (never by assuming
    #   raw ids look a certain way), so re-runs never double-prefix
    # - payload JSON, email_analysis, tasks and jobs are all re-keyed
    # - the FTS index is rebuilt from the re-keyed rows
    try:
        import json as _json
        import re
        from ..mail.identity import (
            parse_email_id, scoped_email_id, is_scoped_for,
        )

        rows = cursor.execute(
            "SELECT id, account_id, payload FROM emails"
        ).fetchall()
        to_migrate = []
        for r in rows:
            local_id = r["id"]
            account_id = r["account_id"]
            if not account_id:
                continue  # Legacy CSV import — has no provider identity
            # Authoritative check first: exact known-account prefix (never
            # depends on provider-id formatting).
            if is_scoped_for(local_id, account_id):
                continue  # Already scoped for this account
            if parse_email_id(local_id)[0] is not None:
                continue  # Scoped for another account — leave untouched
            # Only Gmail-shaped raw ids (hex) are ever re-keyed; anything
            # else is not a provider message id and must stay untouched.
            if not re.fullmatch(r"[0-9a-f]{10,}", local_id):
                continue
            to_migrate.append((local_id, account_id, r["payload"]))

        if to_migrate:
            # Re-keying children before the parent violates immediate FK
            # checks. Run the whole re-key in ONE transaction with
            # deferred foreign keys: SQLite checks them at COMMIT, by
            # which point old and new keys are fully consistent.
            # (defer_foreign_keys is reset by COMMIT and applies only
            # inside the transaction that follows the BEGIN.)
            connection.commit()  # close any ambient transaction

            # Consistent pre-migration backup via the SQLite backup API
            # (WAL-safe snapshot, committed state included). A raw file
            # copy is NOT safe under WAL mode and is never used here.
            # Backup failure ABORTS the migration — user data is never
            # re-keyed without a verified snapshot on disk.
            db_file = connection.execute("PRAGMA database_list").fetchone()["file"]
            # db_file is '' for in-memory test databases
            if db_file:
                backup_file = Path(db_file).with_name(
                    Path(db_file).name + ".pre_id_migration.bak")
                if (backup_file.exists() and backup_file.is_file()
                        and backup_file.stat().st_size > 0):
                    pass  # verified snapshot from the first run — preserved
                else:
                    try:
                        _sqlite_backup(connection, backup_file)
                        print(f"[Alfred] Backed up database before ID migration: {backup_file}")
                    except Exception as exc:
                        import logging as _logging
                        _logging.getLogger("alfred.db").error(
                            "id_migration_backup_failed_aborting: %s", exc,
                            exc_info=True)
                        connection.commit()
                        raise MigrationSafetyError(
                            f"refusing ID migration without a safety snapshot "
                            f"of {db_file}") from exc
            else:
                backup_file = None

            cursor.execute("BEGIN")
            cursor.execute("PRAGMA defer_foreign_keys=ON")

            migrated = 0
            for local_id, account_id, stored_payload in to_migrate:
                raw_id = local_id
                scoped_id = scoped_email_id(account_id, raw_id)
                # Collision guard: a scoped row must not already exist.
                exists = cursor.execute(
                    "SELECT 1 FROM emails WHERE id=?", (scoped_id,)
                ).fetchone()
                if exists:
                    continue
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
                # Update jobs: target_id references email ids for analysis
                # jobs of every type, and analyze job ids carry the email id.
                cursor.execute(
                    "UPDATE jobs SET target_id=? WHERE target_id=?",
                    (scoped_id, raw_id)
                )
                cursor.execute(
                    "UPDATE jobs SET id=? WHERE id=?",
                    (f"analyze_{scoped_id}", f"analyze_{raw_id}")
                )
                # Patch the payload JSON so Email.id reads agree with the
                # new primary key.
                try:
                    payload = _json.loads(stored_payload)
                    payload["id"] = scoped_id
                    new_payload = _json.dumps(payload)
                except Exception:
                    new_payload = stored_payload
                # Update the emails table itself
                cursor.execute(
                    "UPDATE emails SET id=?, payload=? WHERE id=?",
                    (scoped_id, new_payload, raw_id)
                )
                migrated += 1
            if migrated:
                print(f"[Alfred] Migrated {migrated} email IDs to account-prefixed format")
                # Rebuild FTS from the re-keyed rows (single statements —
                # executescript would commit the deferred-FK transaction).
                try:
                    cursor.execute("DROP TABLE IF EXISTS emails_fts")
                    cursor.execute(FTS_SCHEMA if fts_delete_supported(connection)
                                   else FTS_SCHEMA_LEGACY)
                    repopulate_fts_index(connection)
                except Exception as exc:
                    import logging as _logging
                    _logging.getLogger("alfred.fts").warning(
                        "fts_rebuild_after_id_migration_failed: %s", exc)
            connection.commit()
            cursor.execute("PRAGMA defer_foreign_keys=OFF")
    except MigrationSafetyError:
        connection.commit()
        raise  # fail-closed: never swallow the safety gate
    except Exception as exc:
        import logging
        logging.getLogger("alfred.db").warning(
            "scoped_id_migration_failed: %s", exc, exc_info=True
        )  # never silent — migration problems must be visible in logs
    connection.commit()

    # P0-1/P1-3: account-safe threads + provider identity backfill.
    # Runs AFTER the scoped-ID migration so every provider row already has
    # its final (account_id, scoped id). Idempotent: rows already carrying
    # scoped thread ids and provider ids are skipped.
    # - emails.thread_id: raw provider thread id -> scoped local thread id
    # - emails.provider_message_id: backfilled from the scoped id parse
    #   (raw rows keep NULL and stay exempt from the unique index)
    # - tasks.source_thread_id: re-keyed via the linked email's account;
    #   orphan tasks (email gone) are left untouched, never deleted.
    # - emails.payload: patched so payload.id/thread_id/provider_message_id/
    #   account_id agree with the SQL columns (source-of-truth invariant —
    #   Repository.email() deserializes the payload).
    try:
        import json as _json2
        import logging as _logging
        from ..mail.identity import (
            parse_email_id as _parse_id,
            scoped_thread_id as _scoped_thread,
            is_scoped_for as _is_scoped_for,
        )
        _log = _logging.getLogger("alfred.db")
        connection.commit()

        # Pre-scan (read-only): only rows that actually need work. A backup
        # is taken/stored ONLY when this list is non-empty — an empty
        # database must never produce (or be blocked by) a snapshot.
        backfill_work: list[tuple] = []
        for r in cursor.execute(
            "SELECT id, account_id, thread_id, provider_message_id, payload FROM emails"
        ).fetchall():
            local_id, account_id = r["id"], r["account_id"]
            if not account_id:
                continue
            provider = None
            if not r["provider_message_id"]:
                parsed_account, parsed_provider = _parse_id(local_id)
                if parsed_account == account_id and parsed_provider:
                    provider = parsed_provider
            final_provider = provider or r["provider_message_id"]
            scoped_thread = None
            raw_thread = r["thread_id"]
            # Authoritative scoped check: exact known-account prefix. The
            # regex fallback inside is_scoped_for covers genuinely ambiguous
            # legacy ids; non-hex already-scoped ids are never re-prefixed.
            if raw_thread and not _is_scoped_for(raw_thread, account_id):
                scoped_thread = _scoped_thread(account_id, raw_thread)
            final_thread = scoped_thread or raw_thread
            try:
                payload_obj = _json2.loads(r["payload"])
                if not isinstance(payload_obj, dict):
                    payload_obj = None
            except Exception:
                payload_obj = None
            needs_payload = bool(payload_obj is not None and (
                payload_obj.get("id") != local_id
                or payload_obj.get("account_id") != account_id
                or payload_obj.get("thread_id") != final_thread
                or payload_obj.get("provider_message_id") != final_provider
            ))
            if provider or scoped_thread or needs_payload:
                backfill_work.append((local_id, account_id, raw_thread, provider,
                                      scoped_thread, final_thread, final_provider,
                                      payload_obj))

        # Same safety gate as the ID migration: no snapshot, no mutation.
        # (Usually the snapshot already exists from the block above; this
        # covers databases that only need the thread/provider backfill.)
        if backfill_work:
            _db_file = connection.execute("PRAGMA database_list").fetchone()["file"]
            if _db_file:
                _backup_file = Path(_db_file).with_name(
                    Path(_db_file).name + ".pre_id_migration.bak")
                if not (_backup_file.exists() and _backup_file.is_file()
                        and _backup_file.stat().st_size > 0):
                    try:
                        _sqlite_backup(connection, _backup_file)
                        print(f"[Alfred] Backed up database before thread backfill: {_backup_file}")
                    except Exception as exc:
                        _logging.getLogger("alfred.db").error(
                            "thread_backfill_backup_failed_aborting: %s", exc,
                            exc_info=True)
                        connection.commit()
                        raise MigrationSafetyError(
                            f"refusing thread backfill without a safety "
                            f"snapshot of {_db_file}") from exc
            cursor.execute("BEGIN")
            cursor.execute("PRAGMA defer_foreign_keys=ON")

        thread_fixed = 0
        provider_fixed = 0
        payload_fixed = 0
        for (local_id, account_id, raw_thread, provider, scoped_thread,
             final_thread, final_provider, payload_obj) in backfill_work:
            # Provider identity backfill (scoped rows only — never guess).
            if provider:
                cursor.execute(
                    "UPDATE emails SET provider_message_id=? WHERE id=?",
                    (provider, local_id),
                )
                provider_fixed += 1
            # Thread re-key (raw provider thread ids only).
            if scoped_thread:
                cursor.execute(
                    "UPDATE emails SET thread_id=? WHERE id=?",
                    (scoped_thread, local_id),
                )
                cursor.execute(
                    "UPDATE tasks SET source_thread_id=? "
                    "WHERE source_email_id=? AND "
                    "(source_thread_id=? OR source_thread_id IS NULL)",
                    (scoped_thread, local_id, raw_thread),
                )
                thread_fixed += 1
            # Payload consistency: the serialized model agrees with SQL.
            if payload_obj is not None:
                payload_obj["id"] = local_id
                payload_obj["account_id"] = account_id
                payload_obj["thread_id"] = final_thread
                payload_obj["provider_message_id"] = final_provider
                cursor.execute(
                    "UPDATE emails SET payload=? WHERE id=?",
                    (_json2.dumps(payload_obj), local_id),
                )
                payload_fixed += 1
        # Orphan tasks whose source email is gone keep their thread value;
        # only re-key tasks we can attribute to a known account.
        if thread_fixed or provider_fixed or payload_fixed:
            print(f"[Alfred] Thread/provider backfill: {thread_fixed} threads scoped, "
                  f"{provider_fixed} provider ids recorded, "
                  f"{payload_fixed} payloads reconciled")
        connection.commit()
        cursor.execute("PRAGMA defer_foreign_keys=OFF")
    except MigrationSafetyError:
        connection.commit()
        raise  # fail-closed: never swallow the safety gate
    except Exception as exc:
        import logging as _logging2
        _logging2.getLogger("alfred.db").warning(
            "thread_provider_backfill_failed: %s", exc, exc_info=True
        )
    connection.commit()

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

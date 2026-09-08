"""One-shot verification: new migrations against a COPY of production data.

NEVER run against the user's live database — the copy lives in TMP.
"""
import os
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

SRC = Path(os.environ.get("LOCALAPPDATA", "")) / "Alfred" / "alfred.sqlite3"


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="alfred_migcheck_"))
    db = tmp / "prod_copy.sqlite3"
    shutil.copy2(SRC, db)
    print(f"copied {db} ({db.stat().st_size} bytes)")

    from backend.app.db.repositories import Repository
    from backend.app.db.database import fts_table_uses_contentless_delete

    repo = Repository(db)
    con = repo.con

    def q(sql: str):
        return con.execute(sql).fetchone()[0]

    print("emails:", q("SELECT COUNT(*) FROM emails"))
    print("raw threads left:",
          q("SELECT COUNT(*) FROM emails WHERE thread_id IS NOT NULL "
            "AND thread_id NOT LIKE 'gmail_%'"))
    print("scoped threads:",
          q("SELECT COUNT(*) FROM emails WHERE thread_id LIKE 'gmail_%'"))
    print("provider ids filled:",
          q("SELECT COUNT(*) FROM emails WHERE provider_message_id IS NOT NULL"))
    print("tasks total:", q("SELECT COUNT(*) FROM tasks"))
    print("tasks scoped thread:",
          q("SELECT COUNT(*) FROM tasks WHERE source_thread_id LIKE 'gmail_%'"))
    print("analyses:", q("SELECT COUNT(*) FROM email_analysis"))
    print("fts rows:", q("SELECT COUNT(*) FROM emails_fts"))
    print("fts contentless_delete:", fts_table_uses_contentless_delete(con))
    print("unique index present:",
          con.execute("SELECT name FROM sqlite_master WHERE name='idx_emails_account_provider'").fetchone() is not None)

    results = repo.search_emails("invoice")
    print("search 'invoice' rows:", len(results))

    # Draft-context isolation on real shaped data: pick any threaded email.
    row = con.execute(
        "SELECT id, account_id, thread_id FROM emails WHERE thread_id LIKE 'gmail_%' LIMIT 1"
    ).fetchone()
    if row:
        ctx = repo.emails_by_thread(row["thread_id"], account_id=row["account_id"])
        other = [e for e in ctx if e.account_id != row["account_id"]]
        print(f"thread context rows: {len(ctx)}, cross-account leaks: {len(other)}")
        assert not other

    backups = list(tmp.glob("*.bak"))
    print("backup files:", [b.name for b in backups])
    repo.close()
    print("MIGRATION CHECK OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

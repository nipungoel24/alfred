import sqlite3
import shutil
from backend.app.db.repositories import Repository
from backend.app.services.task_migration import TaskMigrationService
from backend.app.schemas import Task
from datetime import datetime, timezone
import os

from pathlib import Path

from pathlib import Path

# 1. Create a fixture database
source_db = r'C:\Users\Nipun\AppData\Local\alfred\alfred.sqlite3'
fixture_db = 'fixture.sqlite3'

import sqlite3
src = sqlite3.connect(source_db)
dst = sqlite3.connect(fixture_db)
with dst:
    src.backup(dst)
src.close()
dst.close()

repo = Repository(Path(fixture_db))

# Mess up the tasks in fixture to simulate "old" derivation
# Insert a dummy pending task that should be deleted
repo.con.execute("INSERT INTO tasks (id, source_email_id, title, status, fingerprint) VALUES ('old_pending', NULL, 'Pending noise', 'pending', 'fp_old_pending')")
# Insert a dummy completed task that should be PRESERVED
repo.con.execute("INSERT INTO tasks (id, source_email_id, title, status, fingerprint) VALUES ('old_completed', NULL, 'Completed noise', 'completed', 'fp_old_completed')")
repo.con.commit()

tasks_init = len(repo.tasks())
print("Fixture Initial Tasks:", tasks_init)

svc = TaskMigrationService(repo)

# 2. Run migration once
print("\n--- FIRST MIGRATION ---")
tasks_before, tasks_after = svc.run_migration("qwen3:4b")
print(f"Tasks Before: {tasks_before}")
print(f"Tasks After: {tasks_after}")

# Verify duplicate tasks = 0
duplicates = repo.con.execute("SELECT fingerprint, count(*) FROM tasks GROUP BY fingerprint HAVING count(*) > 1").fetchall()
print(f"Duplicates: {len(duplicates)}")

# Verify old tasks handled correctly
old_pending = repo.con.execute("SELECT * FROM tasks WHERE id='old_pending'").fetchone()
print("old_pending deleted:", old_pending is None)

old_completed = repo.con.execute("SELECT * FROM tasks WHERE id='old_completed'").fetchone()
print("old_completed preserved:", old_completed is not None)

# Verify accounts/emails preserved
print("Accounts Preserved:", len(repo.con.execute("SELECT * FROM accounts").fetchall()) == 1)
print("Emails Preserved:", len(repo.con.execute("SELECT * FROM emails").fetchall()) == 50)
print("Analysis Preserved:", len(repo.con.execute("SELECT * FROM email_analysis").fetchall()) == 50)

acc = repo.con.execute("SELECT sync_cursor, last_sync_at FROM accounts LIMIT 1").fetchone()
print("Sync cursor preserved:", acc[0] is not None)

# 3. Idempotency (run again)
print("\n--- SECOND MIGRATION ---")
tb2, ta2 = svc.run_migration("qwen3:4b")
print(f"Tasks After Second Migration: {ta2}")
print(f"Difference: {ta2 - tasks_after}")


# 4. Rollback test
print("\n--- ROLLBACK TEST ---")
# Modify service temporarily to crash halfway
original_derive = svc.repo.all_analyses_with_emails
def crashing_analyses(model):
    yield from original_derive(model)
    raise RuntimeError("Simulated crash!")

svc.repo.all_analyses_with_emails = crashing_analyses
try:
    svc.run_migration("qwen3:4b")
except RuntimeError:
    pass

# Verify DB is unchanged
tasks_after_crash = len(repo.tasks())
print("Tasks After Crash:", tasks_after_crash)
print("Rollback successful:", tasks_after_crash == ta2)

repo.close()
os.remove(fixture_db)

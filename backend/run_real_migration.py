from pathlib import Path
from backend.app.db.repositories import Repository
from backend.app.services.task_migration import TaskMigrationService
import sqlite3

db_path = Path(r'C:\Users\Nipun\AppData\Local\alfred\alfred.sqlite3')
repo = Repository(db_path)
svc = TaskMigrationService(repo)

emails = repo.email_count()
print(f"emails={emails}")

tasks_before, tasks_after = svc.run_migration("qwen3:4b")
print(f"tasks_before={tasks_before}")
print(f"tasks_after={tasks_after}")

duplicates = repo.con.execute("SELECT fingerprint, count(*) FROM tasks GROUP BY fingerprint HAVING count(*) > 1").fetchall()
print(f"duplicates={len(duplicates)}")

repo.close()

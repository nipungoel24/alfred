import sys; sys.path.insert(0, '.')
import json
from app.db.repositories import Repository
from app.services.task_derivation import derive_tasks
from app.config import get_settings
from app.schemas import EmailAnalysis
from collections import Counter

s = get_settings()
repo = Repository(s.database_path)

emails = repo.emails()
cur = repo.con.cursor()
analyses_rows = cur.execute("SELECT email_id, payload FROM email_analysis").fetchall()

tasks_after = []
email_counts = Counter()
thread_counts = Counter()

for row in analyses_rows:
    try:
        a = EmailAnalysis.model_validate_json(row[1])
        email = repo.email(row[0])
        if email:
            derived = derive_tasks(email, a)
            for t in derived:
                tasks_after.append({"desc": t.title, "email_id": email.id, "thread_id": email.thread_id})
                email_counts[email.id] += 1
                thread_counts[email.thread_id] += 1
    except Exception as e:
        pass

# Group by description
desc_counter = Counter(t["desc"] for t in tasks_after)
print(f"Total tasks: {len(tasks_after)}")
print("\nTop duplicate descriptions:")
for desc, count in desc_counter.most_common(10):
    if count > 1:
        print(f"[{count}x] {desc}")

print(f"\nUnique thread_ids with tasks: {len(thread_counts)}")

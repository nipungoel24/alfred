import sys; sys.path.insert(0, '.')
import os
from app.db.repositories import Repository
from app.services.task_derivation import derive_tasks
from app.config import get_settings

s = get_settings()
repo = Repository(s.database_path)

emails = repo.emails()
print(f"real_emails_analyzed={len(emails)}")

tasks_before = len(repo.tasks())
print(f"tasks_before_rebuild={tasks_before}")

# Rebuild in memory to count
tasks_after = []
tasks_by_id = {}
high_conf = 0
deadlines = 0
needs_reply_count = 0
failed_analyses = 0

for e in emails:
    fp = e.body  # just need any string for mock here, wait, fp isn't used
    # actually we need the analysis from DB
    analysis = repo.cached_analysis(e.id, "", s.ollama_model) # FP doesn't matter for fetching in our schema, wait, it does!
    # let's just fetch all tasks
    pass

# actually let's just do it directly via DB
cur = repo.con.cursor()
analyses_rows = cur.execute("SELECT email_id, payload FROM email_analysis").fetchall()

from app.schemas import EmailAnalysis
import json

for row in analyses_rows:
    a = EmailAnalysis.model_validate_json(row[1])
    email = repo.email(row[0])
    if email:
        if a.needs_reply:
            needs_reply_count += 1
        if a.deadlines:
            deadlines += len(a.deadlines)
        
        derived = derive_tasks(email, a)
        # Manually deduplicate by id across emails for accurate count since DB isn't used
        for t in derived:
            tasks_by_id[t.id] = t
            if t.confidence == 'high':
                high_conf += 1

tasks_after = list(tasks_by_id.values())
print(f"tasks_after_rebuild={len(tasks_after)}")
print(f"high_confidence_tasks={high_conf}")

# duplicates
seen = set()
dups = 0
for t in tasks_after:
    if t.title in seen:
        dups += 1
    seen.add(t.title)
print(f"duplicate_tasks_after_rebuild={dups}")

print(f"deadlines={deadlines}")
print(f"needs_reply={needs_reply_count}")
print(f"failed_analyses={failed_analyses}")
print(f"average_tasks_per_email={len(tasks_after)/len(emails) if emails else 0:.2f}")


import sys; sys.path.insert(0, '.')
from app.db.repositories import Repository
from app.config import get_settings
from app.schemas import EmailAnalysis
import random

s = get_settings()
repo = Repository(s.database_path)
cur = repo.con.cursor()
analyses_rows = cur.execute("SELECT email_id, payload FROM email_analysis").fetchall()

print("--- Sample of needs_reply = true ---")
nr = []
dl = []
for r in analyses_rows:
    a = EmailAnalysis.model_validate_json(r[1])
    if a.needs_reply:
        nr.append((a.short_summary, a.category.value))
    if a.deadlines:
        dl.append((a.deadlines[0].description, a.deadlines[0].due_at))

random.shuffle(nr)
random.shuffle(dl)

for i in range(min(5, len(nr))):
    print(f"[{nr[i][1]}] {nr[i][0]}")

print("\n--- Sample of deadlines ---")
for i in range(min(5, len(dl))):
    print(f"'{dl[i][0]}' -> '{dl[i][1]}'")

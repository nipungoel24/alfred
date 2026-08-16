import sqlite3

c = sqlite3.connect(r'C:\Users\Nipun\AppData\Local\alfred\alfred.sqlite3')
analysis_count = c.execute('SELECT count(*) FROM email_analysis').fetchone()[0]
tasks_count = c.execute('SELECT count(*) FROM tasks').fetchone()[0]

rows = c.execute("SELECT status, count(*) FROM jobs GROUP BY status").fetchall()
print("Jobs:")
for row in rows:
    print(f"  {row[0]}: {row[1]}")

print(f"Analysis complete: {analysis_count}")
print(f"Tasks derived: {tasks_count}")

# Check duplicates using fingerprint
duplicates = c.execute("""
    SELECT fingerprint, count(*) as count 
    FROM tasks 
    GROUP BY fingerprint 
    HAVING count > 1
""").fetchall()

print(f"Duplicate tasks: {len(duplicates)}")

# Deadlines
deadlines = c.execute("SELECT count(*) FROM tasks WHERE due_at IS NOT NULL").fetchone()[0]
print(f"Deadlines: {deadlines}")

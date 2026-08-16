import sqlite3
import os

db_path = r'C:\Users\Nipun\AppData\Local\alfred\alfred.sqlite3'
c = sqlite3.connect(db_path)

def count(table):
    try:
        return c.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    except Exception as e:
        return f"Error: {e}"

print("accounts:", count("accounts"))
print("emails:", count("emails"))
print("threads:", c.execute("SELECT COUNT(DISTINCT thread_id) FROM emails").fetchone()[0] if count("emails") else 0)
print("email_analysis:", count("email_analysis"))
print("tasks:", count("tasks"))
print("jobs:", count("jobs"))

acc = c.execute("SELECT connection_status, sync_cursor, last_sync_at FROM accounts LIMIT 1").fetchone()
if acc:
    print("sync cursor present:", acc[1] is not None and acc[1] != "")
else:
    print("No accounts found")

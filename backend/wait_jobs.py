import sqlite3
import time

c = sqlite3.connect(r'C:\Users\Nipun\AppData\Local\alfred\alfred.sqlite3')
print('Waiting for jobs...')
start = time.time()
while True:
    rows = c.execute('SELECT status, count(*) FROM jobs GROUP BY status').fetchall()
    print(rows)
    if not any(r[0] in ['queued', 'processing'] for r in rows):
        break
    time.sleep(5)
    print(f'Took {time.time()-start:.1f}s')

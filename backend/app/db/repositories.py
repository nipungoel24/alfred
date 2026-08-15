from datetime import datetime, timezone
import json
from .database import connect
from ..schemas import Email, EmailAnalysis, InboxBriefing, EmailAccount, Task

class Repository:
    def __init__(self, path):
        self.con = connect(path)

    def upsert_email(self, email, fingerprint):
        self.con.execute(
            'INSERT INTO emails (id, payload, content_hash, imported_at, account_id, thread_id) '
            'VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET '
            'payload=excluded.payload, content_hash=excluded.content_hash, imported_at=excluded.imported_at, '
            'account_id=excluded.account_id, thread_id=excluded.thread_id',
            (email.id, email.model_dump_json(), fingerprint, datetime.now(timezone.utc).isoformat(), email.account_id, email.thread_id)
        )
        self.con.commit()

    def emails(self, account_id=None):
        if account_id:
            rows = self.con.execute('SELECT payload FROM emails WHERE account_id=? ORDER BY imported_at DESC', (account_id,)).fetchall()
        else:
            rows = self.con.execute('SELECT payload FROM emails ORDER BY imported_at DESC').fetchall()
        return [Email.model_validate_json(r['payload']) for r in rows]

    def email(self, email_id):
        r = self.con.execute('SELECT payload FROM emails WHERE id=?', (email_id,)).fetchone()
        return Email.model_validate_json(r['payload']) if r else None

    def delete_email(self, email_id):
        self.con.execute('DELETE FROM emails WHERE id=?', (email_id,))
        self.con.execute('DELETE FROM tasks WHERE source_email_id=?', (email_id,))
        self.con.commit()

    def cached_analysis(self, email_id, fingerprint, model, schema='1'):
        r = self.con.execute(
            'SELECT payload FROM email_analysis WHERE email_id=? AND content_hash=? AND model_name=? AND schema_version=?',
            (email_id, fingerprint, model, schema)
        ).fetchone()
        return EmailAnalysis.model_validate_json(r['payload']) if r else None

    def save_analysis(self, email_id, fingerprint, model, analysis, schema='1'):
        self.con.execute(
            'INSERT INTO email_analysis (email_id, content_hash, model_name, schema_version, payload, analyzed_at) '
            'VALUES(?,?,?,?,?,?) ON CONFLICT(email_id) DO UPDATE SET '
            'content_hash=excluded.content_hash, model_name=excluded.model_name, schema_version=excluded.schema_version, '
            'payload=excluded.payload, analyzed_at=excluded.analyzed_at',
            (email_id, fingerprint, model, schema, analysis.model_dump_json(), datetime.now(timezone.utc).isoformat())
        )
        # Extract and save tasks derived from this email analysis
        email = self.email(email_id)
        if email:
            # Action items -> tasks
            for idx, item in enumerate(analysis.action_items):
                t_id = f"task_{email_id}_{idx}"
                if not self.task(t_id):
                    t = Task(
                        id=t_id,
                        source_email_id=email_id,
                        source_thread_id=email.thread_id,
                        title=item.description,
                        description=f"Owner: {item.owner}" if item.owner else None,
                        due_at=item.deadline,
                        priority=analysis.priority.value,
                        status='pending',
                        created_at=datetime.now(timezone.utc).isoformat()
                    )
                    self.save_task(t)
            # Deadlines -> tasks
            for idx, dl in enumerate(analysis.deadlines):
                d_id = f"deadline_{email_id}_{idx}"
                if not self.task(d_id):
                    t = Task(
                        id=d_id,
                        source_email_id=email_id,
                        source_thread_id=email.thread_id,
                        title=dl.description,
                        description=f"Confidence: {dl.confidence}",
                        due_at=dl.due_at,
                        priority=analysis.priority.value,
                        status='pending',
                        created_at=datetime.now(timezone.utc).isoformat()
                    )
                    self.save_task(t)
        self.con.commit()

    def cached_briefing(self, fingerprint, model, schema='1'):
        row = self.con.execute(
            'SELECT payload FROM inbox_briefing WHERE fingerprint=? AND model_name=? AND schema_version=?',
            (fingerprint, model, schema)
        ).fetchone()
        return InboxBriefing.model_validate_json(row['payload']) if row else None

    def save_briefing(self, fingerprint, model, briefing, schema='1'):
        self.con.execute(
            'INSERT INTO inbox_briefing (fingerprint, model_name, schema_version, payload, generated_at) '
            'VALUES(?,?,?,?,?) ON CONFLICT(fingerprint) DO UPDATE SET '
            'model_name=excluded.model_name, schema_version=excluded.schema_version, payload=excluded.payload, '
            'generated_at=excluded.generated_at',
            (fingerprint, model, schema, briefing.model_dump_json(), datetime.now(timezone.utc).isoformat())
        )
        self.con.commit()

    # --- ACCOUNTS ---
    def save_account(self, account: EmailAccount):
        self.con.execute(
            'INSERT INTO accounts (id, provider, email_address, display_name, connection_status, last_sync_at, sync_cursor, created_at, updated_at) '
            'VALUES (?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET '
            'connection_status=excluded.connection_status, last_sync_at=excluded.last_sync_at, '
            'sync_cursor=excluded.sync_cursor, updated_at=excluded.updated_at',
            (
                account.id, account.provider, account.email_address, account.display_name,
                account.connection_status, account.last_sync_at, account.sync_cursor,
                account.created_at or datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat()
            )
        )
        self.con.commit()

    def accounts(self):
        rows = self.con.execute('SELECT * FROM accounts ORDER BY created_at DESC').fetchall()
        return [
            EmailAccount(
                id=r['id'], provider=r['provider'], email_address=r['email_address'],
                display_name=r['display_name'], connection_status=r['connection_status'],
                last_sync_at=r['last_sync_at'], sync_cursor=r['sync_cursor'],
                created_at=r['created_at'], updated_at=r['updated_at']
            )
            for r in rows
        ]

    def account(self, account_id):
        r = self.con.execute('SELECT * FROM accounts WHERE id=?', (account_id,)).fetchone()
        if not r:
            return None
        return EmailAccount(
            id=r['id'], provider=r['provider'], email_address=r['email_address'],
            display_name=r['display_name'], connection_status=r['connection_status'],
            last_sync_at=r['last_sync_at'], sync_cursor=r['sync_cursor'],
            created_at=r['created_at'], updated_at=r['updated_at']
        )

    def delete_account(self, account_id):
        self.con.execute('DELETE FROM accounts WHERE id=?', (account_id,))
        self.con.commit()

    # --- CREDENTIALS ---
    def save_credentials(self, account_id, encrypted_refresh_token, encrypted_access_token, expires_at):
        self.con.execute(
            'INSERT INTO credentials (account_id, encrypted_refresh_token, encrypted_access_token, expires_at) '
            'VALUES (?,?,?,?) ON CONFLICT(account_id) DO UPDATE SET '
            'encrypted_refresh_token=excluded.encrypted_refresh_token, encrypted_access_token=excluded.encrypted_access_token, '
            'expires_at=excluded.expires_at',
            (account_id, encrypted_refresh_token, encrypted_access_token, expires_at)
        )
        self.con.commit()

    def credentials(self, account_id):
        r = self.con.execute(
            'SELECT encrypted_refresh_token, encrypted_access_token, expires_at FROM credentials WHERE account_id=?',
            (account_id,)
        ).fetchone()
        return dict(r) if r else None

    # --- TASKS ---
    def save_task(self, task: Task):
        self.con.execute(
            'INSERT INTO tasks (id, source_email_id, source_thread_id, title, description, due_at, priority, status, created_at) '
            'VALUES (?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET '
            'title=excluded.title, description=excluded.description, due_at=excluded.due_at, '
            'priority=excluded.priority, status=excluded.status',
            (
                task.id, task.source_email_id, task.source_thread_id, task.title, task.description,
                task.due_at, task.priority, task.status, task.created_at or datetime.now(timezone.utc).isoformat()
            )
        )
        self.con.commit()

    def tasks(self):
        rows = self.con.execute('SELECT * FROM tasks ORDER BY created_at DESC').fetchall()
        return [
            Task(
                id=r['id'], source_email_id=r['source_email_id'], source_thread_id=r['source_thread_id'],
                title=r['title'], description=r['description'], due_at=r['due_at'],
                priority=r['priority'], status=r['status'], created_at=r['created_at']
            )
            for r in rows
        ]

    def task(self, task_id):
        r = self.con.execute('SELECT * FROM tasks WHERE id=?', (task_id,)).fetchone()
        if not r:
            return None
        return Task(
            id=r['id'], source_email_id=r['source_email_id'], source_thread_id=r['source_thread_id'],
            title=r['title'], description=r['description'], due_at=r['due_at'],
            priority=r['priority'], status=r['status'], created_at=r['created_at']
        )

    def delete_task(self, task_id):
        self.con.execute('DELETE FROM tasks WHERE id=?', (task_id,))
        self.con.commit()

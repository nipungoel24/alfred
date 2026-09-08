"""Data access layer for Alfred's local SQLite database.

Responsibilities:
- CRUD for emails, analyses, briefings, accounts, credentials, tasks, jobs
- Batch operations with transaction support
- NO business logic (task derivation, AI invocation, etc.)
  EXCEPT mailbox-state persistence, which delegates to the single
  MailEligibilityPolicy module (derivation lives there; this layer only
  stores the derived columns).
"""
from datetime import datetime, timezone
import json
from .database import connect, transaction
from ..schemas import Email, EmailAnalysis, InboxBriefing, EmailAccount, Task, SearchFilters
from ..mail.eligibility import (
    MailEligibilityPolicy, gmail_category_from_labels,
    mailbox_state_from_labels,
)


class Repository:
    def __init__(self, path):
        self.con = connect(path)

    def close(self):
        """Close the database connection."""
        if self.con:
            self.con.close()
            self.con = None

    # ──────────────────────────────────────────────
    # EMAILS
    # ──────────────────────────────────────────────

    def upsert_email(self, email: Email, fingerprint: str):
        """Insert or update a single email. Caller manages transaction."""
        label_ids = list(email.label_ids or [])
        labels = set(label_ids)
        if not labels and not email.account_id:
            # Legacy CSV imports have no Gmail mailbox concept: they are
            # treated as active inbox mail (conceptually INBOX only).
            labels = {'INBOX'}
        state = mailbox_state_from_labels(labels).value
        category = gmail_category_from_labels(labels).value
        eligibility = MailEligibilityPolicy.pipeline_eligibility(labels).value
        self.con.execute(
            'INSERT INTO emails (id, payload, content_hash, imported_at, account_id, thread_id, sender_col, subject_col, received_at_col, '
            'label_ids_json, mailbox_state, gmail_category, pipeline_eligibility) '
            'VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET '
            'payload=excluded.payload, content_hash=excluded.content_hash, imported_at=excluded.imported_at, '
            'account_id=excluded.account_id, thread_id=excluded.thread_id, '
            'sender_col=excluded.sender_col, subject_col=excluded.subject_col, received_at_col=excluded.received_at_col, '
            'label_ids_json=excluded.label_ids_json, mailbox_state=excluded.mailbox_state, '
            'gmail_category=excluded.gmail_category, pipeline_eligibility=excluded.pipeline_eligibility',
            (email.id, email.model_dump_json(), fingerprint,
             datetime.now(timezone.utc).isoformat(), email.account_id, email.thread_id,
             email.sender.lower(), email.subject, email.received_at.isoformat() if email.received_at else None,
             json.dumps(label_ids), state, category, eligibility)
        )
        self._update_fts_one(email.id, email)

    def upsert_email_commit(self, email: Email, fingerprint: str):
        """Insert or update a single email with immediate commit."""
        self.upsert_email(email, fingerprint)
        self.con.commit()

    def upsert_emails_batch(self, email_fingerprint_pairs: list[tuple[Email, str]]):
        """Batch insert/update emails in a single transaction."""
        with transaction(self.con) as _:
            for email, fingerprint in email_fingerprint_pairs:
                self.upsert_email(email, fingerprint)

    def emails(self, account_id=None, limit=500, offset=0):
        """Fetch emails ordered by received_at descending."""
        if account_id:
            rows = self.con.execute(
                'SELECT payload FROM emails WHERE account_id=? ORDER BY received_at_col DESC LIMIT ? OFFSET ?',
                (account_id, limit, offset)
            ).fetchall()
        else:
            rows = self.con.execute(
                'SELECT payload FROM emails ORDER BY received_at_col DESC LIMIT ? OFFSET ?',
                (limit, offset)
            ).fetchall()
        return [Email.model_validate_json(r['payload']) for r in rows]

    def email_count(self, account_id=None) -> int:
        """Get total email count, optionally filtered by account."""
        if account_id:
            return self.con.execute('SELECT COUNT(*) FROM emails WHERE account_id=?', (account_id,)).fetchone()[0]
        return self.con.execute('SELECT COUNT(*) FROM emails').fetchone()[0]

    def email(self, email_id: str):
        r = self.con.execute('SELECT payload FROM emails WHERE id=?', (email_id,)).fetchone()
        return Email.model_validate_json(r['payload']) if r else None

    def email_exists(self, email_id: str) -> bool:
        """Check if email exists without deserializing payload."""
        r = self.con.execute('SELECT 1 FROM emails WHERE id=? LIMIT 1', (email_id,)).fetchone()
        return r is not None

    def email_eligibility(self, email_id: str) -> dict | None:
        """Persisted eligibility projection for one message.

        These columns are recomputed on every label change and are the
        single source of truth for pipeline policy at runtime (they
        include the non-Gmail legacy-import fallback).
        """
        r = self.con.execute(
            'SELECT mailbox_state, gmail_category, pipeline_eligibility, label_ids_json '
            'FROM emails WHERE id=?', (email_id,)
        ).fetchone()
        if not r:
            return None
        labels = []
        try:
            if r['label_ids_json']:
                labels = json.loads(r['label_ids_json'])
        except Exception:
            pass
        return {
            'mailbox_state': r['mailbox_state'],
            'gmail_category': r['gmail_category'],
            'pipeline_eligibility': r['pipeline_eligibility'],
            'label_ids': labels,
        }

    def update_email_labels(self, email_id: str, label_ids: list[str]) -> bool:
        """Recompute mailbox state / category / eligibility for a message.

        Used by Gmail history labelAdded/labelRemoved events and metadata
        refreshes. Source payload is NOT destroyed — only eligibility is.
        Returns False when the message is not cached locally.
        """
        labels = set(label_ids or [])
        state = mailbox_state_from_labels(labels).value
        category = gmail_category_from_labels(labels).value
        eligibility = MailEligibilityPolicy.pipeline_eligibility(labels).value
        cur = self.con.execute(
            'UPDATE emails SET label_ids_json=?, mailbox_state=?, gmail_category=?, pipeline_eligibility=? '
            'WHERE id=?',
            (json.dumps(sorted(labels)), state, category, eligibility, email_id)
        )
        if cur.rowcount == 0:
            self.con.commit()
            return False
        # Keep the in-payload label_ids consistent for future reads.
        row = self.con.execute('SELECT payload FROM emails WHERE id=?', (email_id,)).fetchone()
        if row:
            try:
                email = Email.model_validate_json(row['payload'])
                email.label_ids = sorted(labels)
                self.con.execute('UPDATE emails SET payload=? WHERE id=?',
                                 (email.model_dump_json(), email_id))
            except Exception:
                pass
        self.con.commit()
        return True

    def mark_email_excluded(self, email_id: str) -> bool:
        """Exclude a cached message from all current-attention projections.

        Used when Gmail reports permanent deletion (messagesDeleted): the
        source row is preserved for history/thread integrity but can no
        longer feed briefing, tasks, deadlines, needs-reply, or the queue.
        """
        cur = self.con.execute(
            'UPDATE emails SET mailbox_state=?, pipeline_eligibility=? WHERE id=?',
            ('trash', 'excluded', email_id)
        )
        self.con.commit()
        return cur.rowcount > 0

    def emails_missing_labels(self, account_id: str | None = None, limit: int = 200) -> list[str]:
        """IDs of cached Gmail messages whose label set is unknown.

        Only provider-sourced rows are eligible for metadata refresh;
        legacy CSV imports (no account) never need it.
        """
        if account_id:
            rows = self.con.execute(
                'SELECT id FROM emails WHERE account_id=? AND label_ids_json IS NULL LIMIT ?',
                (account_id, limit)
            ).fetchall()
        else:
            rows = self.con.execute(
                'SELECT id FROM emails WHERE account_id IS NOT NULL AND label_ids_json IS NULL LIMIT ?',
                (limit,)
            ).fetchall()
        return [r['id'] for r in rows]

    def emails_filtered(self, account_id: str | None = None,
                        category: str | None = None,
                        mailbox_state: str | None = None,
                        scope: str = 'inbox',
                        kind: str | None = None,
                        include_excluded: bool = False,
                        query: str | None = None,
                        priority: str | None = None,
                        needs_reply: bool | None = None,
                        limit: int = 200, offset: int = 0) -> list[Email]:
        """Fetch emails with typed filters, DB-side (no JS filtering).

        Scopes:
        - 'inbox' (default): active Gmail INBOX only; category tabs apply.
        - 'all': the real All Mail — received inbox, archived received,
          AND sent messages. Spam/Trash/Draft never appear. `kind` refines
          it (received | sent | archived); `category` is ignored here
          (Gmail tab semantics belong to the Inbox experience).
        - include_excluded=True bypasses the scope (internal use only).

        Archived/sent visibility never widens intelligence eligibility —
        those stay inbox-only per MailEligibilityPolicy.
        """
        sql = 'SELECT payload FROM emails WHERE 1=1'
        params: list = []
        if account_id:
            sql += ' AND account_id=?'
            params.append(account_id)
        if include_excluded:
            if mailbox_state:
                sql += ' AND mailbox_state=?'
                params.append(mailbox_state)
        elif scope == 'all':
            if kind == 'received':
                sql += ' AND mailbox_state IN ("active_inbox","archived")'
            elif kind == 'sent':
                sql += ' AND mailbox_state="sent"'
            elif kind == 'archived':
                sql += ' AND mailbox_state="archived"'
            else:
                sql += ' AND mailbox_state IN ("active_inbox","archived","sent")'
        else:
            sql += ' AND mailbox_state="active_inbox"'
        if category and scope != 'all':
            sql += ' AND gmail_category=?'
            params.append(category)
        if query:
            # Category-contextual search (substring on indexed subject/sender
            # columns; FTS path keeps full-text ranking for broad searches).
            like = f'%{query}%'
            sql += ' AND (subject_col LIKE ? OR sender_col LIKE ?)'
            params.extend([like, like])
        # Priority and needs_reply filtering: applied BEFORE LIMIT/OFFSET
        # via the analysis table join (no Python post-filtering of truncated windows).
        if priority or needs_reply is not None:
            sql += ' AND id IN (SELECT a.email_id FROM email_analysis a WHERE a.email_id = id'
            analysis_params: list = []
            if priority:
                if priority == 'high':
                    sql += ' AND json_extract(a.payload, "$.priority") IN ("high","urgent")'
                else:
                    sql += ' AND json_extract(a.payload, "$.priority") = ?'
                    analysis_params.append(priority)
            if needs_reply is not None:
                sql += ' AND json_extract(a.payload, "$.needs_reply") = ?'
                analysis_params.append(1 if needs_reply else 0)
            sql += ')'
            params.extend(analysis_params)
        sql += ' ORDER BY received_at_col DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        rows = self.con.execute(sql, params).fetchall()
        return [Email.model_validate_json(r['payload']) for r in rows]

    def email_counts(self, account_id: str | None = None) -> dict:
        """Scope + category counts derived from stored Gmail labels.

        - inbox: active Gmail INBOX messages
        - all_mail: inbox + archived received + sent (the real All Mail;
          spam/trash/draft excluded)
        - excluded: everything outside all_mail
        - categories: inbox-scoped tab counts (tab semantics belong to
          the Inbox experience)
        """
        acct_where = 'account_id=?' if account_id else '1=1'
        params = (account_id,) if account_id else ()

        active_inbox = self.con.execute(
            f'SELECT COUNT(*) FROM emails WHERE {acct_where} AND mailbox_state="active_inbox"',
            params
        ).fetchone()[0]
        all_mail = self.con.execute(
            f'SELECT COUNT(*) FROM emails WHERE {acct_where} '
            'AND mailbox_state IN ("active_inbox","archived","sent")',
            params
        ).fetchone()[0]
        excluded = self.con.execute(
            f'SELECT COUNT(*) FROM emails WHERE {acct_where} '
            'AND mailbox_state NOT IN ("active_inbox","archived","sent")',
            params
        ).fetchone()[0]
        rows = self.con.execute(
            f'SELECT gmail_category, COUNT(*) FROM emails '
            f'WHERE {acct_where} AND mailbox_state="active_inbox" GROUP BY gmail_category',
            params
        ).fetchall()
        category_counts = {'primary': 0, 'promotions': 0, 'social': 0, 'updates': 0, 'forums': 0}
        for r in rows:
            cat = r[0] or 'primary'
            if cat in category_counts:
                category_counts[cat] = r[1]
        return {'active_inbox': active_inbox,
                'all_mail': all_mail,
                'excluded': excluded,
                'categories': category_counts}

    def eligible_emails_without_analysis(self, model: str, schema='1',
                                         account_id: str | None = None) -> list[Email]:
        """ACTIVE-Inbox messages that still need analysis (for the queue).

        Never schedules excluded (spam/trash/draft/sent/archived) mail.
        """
        where = 'WHERE e.mailbox_state="active_inbox"'
        params: list = [model, schema]
        if account_id:
            where += ' AND e.account_id=?'
            params.append(account_id)
        rows = self.con.execute(
            'SELECT e.payload FROM emails e LEFT JOIN email_analysis a '
            'ON a.email_id = e.id AND a.model_name=? AND a.schema_version=? '
            + where + ' AND a.email_id IS NULL',
            tuple(params)
        ).fetchall()
        return [Email.model_validate_json(r['payload']) for r in rows]

    def delete_email(self, email_id: str):
        """Delete an email and its FTS entry."""
        # Delete from FTS first (contentless_delete=1 supports per-row DELETE)
        row = self.con.execute("SELECT rowid FROM emails WHERE id=?", (email_id,)).fetchone()
        if row:
            try:
                self.con.execute("DELETE FROM emails_fts WHERE rowid=?", (row[0],))
            except Exception:
                pass  # FTS5 not available
        self.con.execute('DELETE FROM emails WHERE id=?', (email_id,))
        self.con.execute('DELETE FROM tasks WHERE source_email_id=?', (email_id,))
        self.con.commit()

    def search_emails(self, query: str, limit=100) -> list[Email]:
        """Full-text search using FTS5 if available, falling back to LIKE.

        Global search covers the FULL synchronized mailbox: active inbox,
        archived received, and sent messages. Spam/trash/draft rows never
        surface through search. Uses BM25 ranking for better relevance.
        """
        try:
            # Use BM25 ranking for better relevance
            rows = self.con.execute(
                "SELECT e.payload, bm25(emails_fts) as rank FROM emails_fts f "
                "JOIN emails e ON f.rowid = e.rowid "
                "WHERE emails_fts MATCH ? "
                "AND e.mailbox_state IN ('active_inbox','archived','sent') "
                "ORDER BY rank LIMIT ?",
                (query, limit)
            ).fetchall()
            return [Email.model_validate_json(r['payload']) for r in rows]
        except Exception:
            # FTS5 not available, fall back to LIKE search
            like_q = f"%{query}%"
            rows = self.con.execute(
                "SELECT payload FROM emails "
                "WHERE mailbox_state IN ('active_inbox','archived','sent') "
                "AND (sender_col LIKE ? OR subject_col LIKE ?) LIMIT ?",
                (like_q, like_q, limit)
            ).fetchall()
            return [Email.model_validate_json(r['payload']) for r in rows]

    def search_emails_structured(self, filters: SearchFilters, account_id: str | None = None,
                                 limit=100, offset: int = 0) -> list[Email]:
        """Structured search with filters applied at the database level.

        Filters are applied BEFORE LIMIT/OFFSET for correct results.
        Uses BM25 ranking when FTS5 is available.
        """
        conditions = ["e.mailbox_state IN ('active_inbox','archived','sent')"]
        params: list = []
        
        # Apply account filter
        if account_id:
            conditions.append("e.account_id = ?")
            params.append(account_id)
        
        # Apply sender filter
        if filters.sender:
            conditions.append("e.sender_col LIKE ?")
            params.append(f"%{filters.sender}%")
        
        # Apply subject filter
        if filters.subject:
            conditions.append("e.subject_col LIKE ?")
            params.append(f"%{filters.subject}%")
        
        # Apply date filters
        if filters.after:
            conditions.append("e.received_at_col >= ?")
            params.append(filters.after)
        if filters.before:
            conditions.append("e.received_at_col <= ?")
            params.append(filters.before)
        
        # Apply category filter
        if filters.category:
            conditions.append("e.gmail_category = ?")
            params.append(filters.category)
        
        # Apply mailbox state filter
        if filters.mailbox_state:
            conditions.append("e.mailbox_state = ?")
            params.append(filters.mailbox_state)
        
        # Build WHERE clause
        where_clause = " AND ".join(conditions)
        
        # Build FTS5 MATCH clause for free text
        fts_match = None
        if filters.free_text:
            fts_match = " ".join(filters.free_text)
        
        try:
            if fts_match:
                # Use FTS5 with BM25 ranking
                rows = self.con.execute(
                    f"SELECT e.payload, bm25(emails_fts) as rank FROM emails_fts f "
                    f"JOIN emails e ON f.rowid = e.rowid "
                    f"WHERE emails_fts MATCH ? "
                    f"AND {where_clause} "
                    f"ORDER BY rank LIMIT ? OFFSET ?",
                    (fts_match, *params, limit, offset)
                ).fetchall()
            else:
                # No free text, just apply filters
                rows = self.con.execute(
                    f"SELECT e.payload FROM emails e "
                    f"WHERE {where_clause} "
                    f"ORDER BY e.received_at_col DESC LIMIT ? OFFSET ?",
                    (*params, limit, offset)
                ).fetchall()
            
            return [Email.model_validate_json(r['payload']) for r in rows]
        except Exception:
            # Fallback to simple search
            return self.search_emails(query=' '.join(filters.free_text), limit=limit)

    def emails_by_thread(self, thread_id: str) -> list[Email]:
        """Fetch emails in a thread, ordered chronologically."""
        rows = self.con.execute(
            'SELECT payload FROM emails WHERE thread_id=? ORDER BY received_at_col ASC',
            (thread_id,)
        ).fetchall()
        return [Email.model_validate_json(r['payload']) for r in rows]

    def _update_fts_one(self, email_id: str, email: Email):
        """Keep the FTS5 index in sync for a single upsert.

        Uses contentless-delete FTS5 (contentless_delete=1) which supports
        per-row DELETE operations. No full rebuild needed on content changes.
        - New emails: INSERT directly into FTS
        - Updated emails (content changed): DELETE old entry + INSERT new
        - Updated emails (no content change): skip (FTS already correct)
        - Deleted emails: handled by delete_email() which does DELETE directly
        """
        try:
            # Get the rowid for this email
            row = self.con.execute(
                "SELECT rowid FROM emails WHERE id=?", (email_id,)
            ).fetchone()
            if not row:
                return
            rowid = row[0]

            # Check if FTS entry already exists for this rowid
            existing = self.con.execute(
                "SELECT rowid FROM emails_fts WHERE rowid=?",
                (rowid,)
            ).fetchone()
            if existing:
                # Entry exists — check if content actually changed
                # by comparing subject/sender (cheap proxy for body changes)
                old = self.con.execute(
                    "SELECT subject, sender FROM emails_fts WHERE rowid=?",
                    (rowid,)
                ).fetchone()
                if old and old[0] == email.subject and old[1] == email.sender:
                    return  # No content change, FTS is current
                # Content changed: delete old entry and insert new one
                self.con.execute("DELETE FROM emails_fts WHERE rowid=?", (rowid,))
                self.con.execute(
                    "INSERT INTO emails_fts(rowid, subject, sender, body) VALUES (?, ?, ?, ?)",
                    (rowid, email.subject, email.sender, email.body[:5000] if email.body else '')
                )
                return
            
            # New email: insert into FTS
            self.con.execute(
                "INSERT INTO emails_fts(rowid, subject, sender, body) VALUES (?, ?, ?, ?)",
                (rowid, email.subject, email.sender, email.body[:5000] if email.body else '')
            )
        except Exception:
            pass  # FTS5 not available

    def rebuild_fts(self):
        """Rebuild the FTS5 index from the emails table.

        For contentless FTS5, we need to drop and recreate the table
        to remove orphaned entries and ensure the index is in sync.
        Should be called periodically or after bulk DELETE operations.
        """
        try:
            # Get all rowids and content from emails table
            emails = self.con.execute(
                "SELECT rowid, subject_col, sender_col, payload FROM emails"
            ).fetchall()
            
            # Drop and recreate FTS5 table
            self.con.execute("DROP TABLE IF EXISTS emails_fts")
            self.con.execute("""
                CREATE VIRTUAL TABLE emails_fts USING fts5(
                    subject,
                    sender,
                    body,
                    content='',
                    tokenize='unicode61'
                )
            """)
            
            # Re-insert all emails into FTS5
            for rowid, subject, sender, payload in emails:
                try:
                    # Extract body from payload (truncated to 5000 chars)
                    import json
                    data = json.loads(payload)
                    body = data.get('body', '')[:5000] if data.get('body') else ''
                    self.con.execute(
                        "INSERT INTO emails_fts(rowid, subject, sender, body) VALUES (?, ?, ?, ?)",
                        (rowid, subject, sender, body)
                    )
                except Exception:
                    continue
        except Exception:
            pass  # FTS5 not available

    # ──────────────────────────────────────────────
    # ANALYSIS
    # ──────────────────────────────────────────────

    def cached_analysis(self, email_id: str, fingerprint: str, model: str, schema='1'):
        r = self.con.execute(
            'SELECT payload FROM email_analysis WHERE email_id=? AND content_hash=? AND model_name=? AND schema_version=?',
            (email_id, fingerprint, model, schema)
        ).fetchone()
        return EmailAnalysis.model_validate_json(r['payload']) if r else None

    def save_analysis(self, email_id: str, fingerprint: str, model: str, analysis: EmailAnalysis, schema='1'):
        """Save analysis result. Does NOT create tasks — that is TaskDerivationService's job."""
        self.con.execute(
            'INSERT INTO email_analysis (email_id, content_hash, model_name, schema_version, payload, analyzed_at) '
            'VALUES(?,?,?,?,?,?) ON CONFLICT(email_id) DO UPDATE SET '
            'content_hash=excluded.content_hash, model_name=excluded.model_name, schema_version=excluded.schema_version, '
            'payload=excluded.payload, analyzed_at=excluded.analyzed_at',
            (email_id, fingerprint, model, schema, analysis.model_dump_json(), datetime.now(timezone.utc).isoformat())
        )
        self.con.commit()

    def all_analyses_with_emails(self, model: str, schema='1') -> list[tuple[Email, EmailAnalysis]]:
        """Load all email+analysis pairs efficiently in a single query."""
        rows = self.con.execute(
            'SELECT e.payload AS email_payload, a.payload AS analysis_payload '
            'FROM emails e JOIN email_analysis a ON e.id = a.email_id '
            'WHERE a.model_name=? AND a.schema_version=?',
            (model, schema)
        ).fetchall()
        results = []
        for r in rows:
            email = Email.model_validate_json(r['email_payload'])
            analysis = EmailAnalysis.model_validate_json(r['analysis_payload'])
            email.analysis = analysis
            results.append((email, analysis))
        return results

    # ──────────────────────────────────────────────
    # BRIEFINGS
    # ──────────────────────────────────────────────

    def cached_briefing(self, fingerprint: str, model: str, schema='1'):
        row = self.con.execute(
            'SELECT payload FROM inbox_briefing WHERE fingerprint=? AND model_name=? AND schema_version=?',
            (fingerprint, model, schema)
        ).fetchone()
        return InboxBriefing.model_validate_json(row['payload']) if row else None

    def save_briefing(self, fingerprint: str, model: str, briefing: InboxBriefing, schema='1'):
        self.con.execute(
            'INSERT INTO inbox_briefing (fingerprint, model_name, schema_version, payload, generated_at) '
            'VALUES(?,?,?,?,?) ON CONFLICT(fingerprint) DO UPDATE SET '
            'model_name=excluded.model_name, schema_version=excluded.schema_version, payload=excluded.payload, '
            'generated_at=excluded.generated_at',
            (fingerprint, model, schema, briefing.model_dump_json(), datetime.now(timezone.utc).isoformat())
        )
        self.con.commit()

    # ──────────────────────────────────────────────
    # ACCOUNTS
    # ──────────────────────────────────────────────

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

    def account(self, account_id: str):
        r = self.con.execute('SELECT * FROM accounts WHERE id=?', (account_id,)).fetchone()
        if not r:
            return None
        return EmailAccount(
            id=r['id'], provider=r['provider'], email_address=r['email_address'],
            display_name=r['display_name'], connection_status=r['connection_status'],
            last_sync_at=r['last_sync_at'], sync_cursor=r['sync_cursor'],
            created_at=r['created_at'], updated_at=r['updated_at']
        )

    def delete_account(self, account_id: str):
        self.con.execute('DELETE FROM accounts WHERE id=?', (account_id,))
        self.con.commit()

    # ──────────────────────────────────────────────
    # CREDENTIALS
    # ──────────────────────────────────────────────

    def save_credentials(self, account_id: str, encrypted_refresh_token, encrypted_access_token, expires_at: str):
        self.con.execute(
            'INSERT INTO credentials (account_id, encrypted_refresh_token, encrypted_access_token, expires_at) '
            'VALUES (?,?,?,?) ON CONFLICT(account_id) DO UPDATE SET '
            'encrypted_refresh_token=excluded.encrypted_refresh_token, encrypted_access_token=excluded.encrypted_access_token, '
            'expires_at=excluded.expires_at',
            (account_id, encrypted_refresh_token, encrypted_access_token, expires_at)
        )
        self.con.commit()

    def credentials(self, account_id: str):
        r = self.con.execute(
            'SELECT encrypted_refresh_token, encrypted_access_token, expires_at FROM credentials WHERE account_id=?',
            (account_id,)
        ).fetchone()
        return dict(r) if r else None

    # ──────────────────────────────────────────────
    # TASKS
    # ──────────────────────────────────────────────

    def save_task(self, task: Task):
        self.con.execute(
            'INSERT INTO tasks (id, source_email_id, source_thread_id, title, description, due_at, priority, status, created_at, '
            'derivation_version, confidence, fingerprint) '
            'VALUES (?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET '
            'title=excluded.title, description=excluded.description, due_at=excluded.due_at, '
            'priority=excluded.priority, status=excluded.status, '
            'derivation_version=excluded.derivation_version, confidence=excluded.confidence, fingerprint=excluded.fingerprint',
            (
                task.id, task.source_email_id, task.source_thread_id, task.title, task.description,
                task.due_at, task.priority, task.status,
                task.created_at or datetime.now(timezone.utc).isoformat(),
                getattr(task, 'derivation_version', '1'),
                getattr(task, 'confidence', 'medium'),
                getattr(task, 'fingerprint', None)
            )
        )
        self.con.commit()

    def save_tasks_batch(self, tasks_list: list[Task]):
        """Save multiple tasks in a single transaction."""
        with transaction(self.con) as _:
            for task in tasks_list:
                self.con.execute(
                    'INSERT INTO tasks (id, source_email_id, source_thread_id, title, description, due_at, priority, status, created_at, '
                    'derivation_version, confidence, fingerprint) '
                    'VALUES (?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET '
                    'title=excluded.title, description=excluded.description, due_at=excluded.due_at, '
                    'priority=excluded.priority, status=excluded.status, '
                    'derivation_version=excluded.derivation_version, confidence=excluded.confidence, fingerprint=excluded.fingerprint',
                    (
                        task.id, task.source_email_id, task.source_thread_id, task.title, task.description,
                        task.due_at, task.priority, task.status,
                        task.created_at or datetime.now(timezone.utc).isoformat(),
                        getattr(task, 'derivation_version', '2'),
                        getattr(task, 'confidence', 'medium'),
                        getattr(task, 'fingerprint', None)
                    )
                )

    def tasks(self, status=None):
        if status:
            rows = self.con.execute(
                'SELECT * FROM tasks WHERE status=? ORDER BY created_at DESC', (status,)
            ).fetchall()
        else:
            rows = self.con.execute('SELECT * FROM tasks ORDER BY created_at DESC').fetchall()
        return [self._task_from_row(r) for r in rows]

    def active_tasks(self, status=None) -> list[Task]:
        """Current-attention task projection.

        Tasks whose source email is no longer pipeline-eligible (spam,
        trash, draft, sent-only, archived) are hidden from the ACTIVE
        projection but their rows are preserved. Tasks without a source
        email (user-created) always appear.
        """
        sql = (
            'SELECT t.* FROM tasks t LEFT JOIN emails e ON e.id = t.source_email_id '
            'WHERE (t.source_email_id IS NULL OR e.mailbox_state = "active_inbox")'
        )
        params: tuple = ()
        if status:
            sql += ' AND t.status=?'
            params = (status,)
        sql += ' ORDER BY t.created_at DESC'
        rows = self.con.execute(sql, params).fetchall()
        return [self._task_from_row(r) for r in rows]

    def tasks_by_thread(self, thread_id: str) -> list[Task]:
        """Get tasks linked to a specific thread."""
        rows = self.con.execute(
            'SELECT * FROM tasks WHERE source_thread_id=?', (thread_id,)
        ).fetchall()
        return [self._task_from_row(r) for r in rows]

    def tasks_by_email(self, email_id: str) -> list[Task]:
        """Get tasks linked to a specific email."""
        rows = self.con.execute(
            'SELECT * FROM tasks WHERE source_email_id=?', (email_id,)
        ).fetchall()
        return [self._task_from_row(r) for r in rows]

    def task(self, task_id: str):
        r = self.con.execute('SELECT * FROM tasks WHERE id=?', (task_id,)).fetchone()
        return self._task_from_row(r) if r else None

    def task_exists_by_fingerprint(self, fingerprint: str) -> bool:
        """Check if a task with this fingerprint already exists."""
        r = self.con.execute('SELECT 1 FROM tasks WHERE fingerprint=? LIMIT 1', (fingerprint,)).fetchone()
        return r is not None

    def delete_task(self, task_id: str):
        self.con.execute('DELETE FROM tasks WHERE id=?', (task_id,))
        self.con.commit()

    def delete_tasks_by_derivation_version(self, version: str):
        """Delete all tasks created by a specific derivation version."""
        self.con.execute('DELETE FROM tasks WHERE derivation_version=?', (version,))
        self.con.commit()

    def _task_from_row(self, r) -> Task:
        task = Task(
            id=r['id'], source_email_id=r['source_email_id'], source_thread_id=r['source_thread_id'],
            title=r['title'], description=r['description'], due_at=r['due_at'],
            priority=r['priority'], status=r['status'], created_at=r['created_at']
        )
        task.derivation_version = r['derivation_version']
        task.confidence = r['confidence']
        task.fingerprint = r['fingerprint']
        return task

    # ──────────────────────────────────────────────
    # JOBS
    # ──────────────────────────────────────────────

    def enqueue_job(self, job_id: str, job_type: str, target_id: str, priority: int = 50,
                    not_before: str | None = None):
        """Enqueue a background job. Idempotent — skips if job already exists."""
        self.con.execute(
            'INSERT OR IGNORE INTO jobs (id, job_type, target_id, priority, status, created_at, not_before) '
            'VALUES (?,?,?,?,?,?,?)',
            (job_id, job_type, target_id, priority, 'queued',
             datetime.now(timezone.utc).isoformat(), not_before)
        )
        self.con.commit()

    def next_job(self, job_type: str = None, now_iso: str | None = None):
        """Get the next queued job by priority, honouring not_before.

        Jobs whose not_before timestamp is still in the future are not
        returned — this is how the backfill worker rate-limits itself
        (bounded page + scheduled next page) without blocking polling.
        """
        now_iso = now_iso or datetime.now(timezone.utc).isoformat()
        if job_type:
            r = self.con.execute(
                'SELECT * FROM jobs WHERE status="queued" AND job_type=? '
                'AND (not_before IS NULL OR not_before <= ?) '
                'ORDER BY priority DESC, created_at ASC LIMIT 1',
                (job_type, now_iso)
            ).fetchone()
        else:
            r = self.con.execute(
                'SELECT * FROM jobs WHERE status="queued" '
                'AND (not_before IS NULL OR not_before <= ?) '
                'ORDER BY priority DESC, created_at ASC LIMIT 1',
                (now_iso,)
            ).fetchone()
        return dict(r) if r else None

    def requeue_job(self, job_id: str, not_before: str | None = None):
        """Re-arm a job for its next bounded run (resets attempts/errors).

        Used by the backfill worker after each successful page: the same
        durable job row is re-queued with a not_before rate-limit instead
        of creating new rows forever.
        """
        self.con.execute(
            'UPDATE jobs SET status="queued", attempts=0, started_at=NULL, '
            'completed_at=NULL, error_code=NULL, error_message=NULL, not_before=? '
            'WHERE id=?',
            (not_before, job_id)
        )
        self.con.commit()

    def rearm_terminal_job(self, job_id: str):
        """Re-arm a job row that finished or paused, when work remains.

        Covers the resume path: a 'succeeded'/'cancelled'/'failed'/'paused'
        row becomes queued again (attempts reset, backoff cleared). Rows
        that are currently queued/running or in retry backoff are left
        untouched.
        """
        self.con.execute(
            'UPDATE jobs SET status="queued", attempts=0, not_before=NULL, '
            'started_at=NULL, completed_at=NULL, error_code=NULL, error_message=NULL '
            "WHERE id=? AND status IN ('succeeded','cancelled','failed','paused')",
            (job_id,)
        )
        self.con.commit()

    def retry_job_with_backoff(self, job_id: str, error_code: str, error_message: str,
                               not_before: str):
        """Mark a job retryable_failed with a not_before backoff timestamp."""
        self.con.execute(
            'UPDATE jobs SET status="retryable_failed", completed_at=?, error_code=?, '
            'error_message=?, not_before=? WHERE id=?',
            (datetime.now(timezone.utc).isoformat(), error_code, error_message,
             not_before, job_id)
        )
        self.con.commit()

    def job(self, job_id: str):
        r = self.con.execute('SELECT * FROM jobs WHERE id=?', (job_id,)).fetchone()
        return dict(r) if r else None

    def update_job_status(self, job_id: str, status: str, error_code: str = None, error_message: str = None):
        now = datetime.now(timezone.utc).isoformat()
        if status == 'running':
            self.con.execute(
                'UPDATE jobs SET status=?, started_at=?, attempts=attempts+1 WHERE id=?',
                (status, now, job_id)
            )
        elif status in ('succeeded', 'failed', 'retryable_failed'):
            self.con.execute(
                'UPDATE jobs SET status=?, completed_at=?, error_code=?, error_message=? WHERE id=?',
                (status, now, error_code, error_message, job_id)
            )
        else:
            self.con.execute('UPDATE jobs SET status=? WHERE id=?', (status, job_id))
        self.con.commit()

    def pending_job_count(self, job_type: str = None) -> int:
        if job_type:
            return self.con.execute(
                'SELECT COUNT(*) FROM jobs WHERE status IN ("queued","running") AND job_type=?', (job_type,)
            ).fetchone()[0]
        return self.con.execute(
            'SELECT COUNT(*) FROM jobs WHERE status IN ("queued","running")'
        ).fetchone()[0]

    def completed_job_count(self, job_type: str = None) -> int:
        if job_type:
            return self.con.execute(
                'SELECT COUNT(*) FROM jobs WHERE status="succeeded" AND job_type=?', (job_type,)
            ).fetchone()[0]
        return self.con.execute(
            'SELECT COUNT(*) FROM jobs WHERE status="succeeded"'
        ).fetchone()[0]

    def failed_job_count(self, job_type: str = None) -> int:
        if job_type:
            return self.con.execute(
                'SELECT COUNT(*) FROM jobs WHERE status IN ("failed","retryable_failed") AND job_type=?', (job_type,)
            ).fetchone()[0]
        return self.con.execute(
            'SELECT COUNT(*) FROM jobs WHERE status IN ("failed","retryable_failed")'
        ).fetchone()[0]

    def reset_retryable_jobs(self):
        """Reset retryable_failed jobs back to queued if under max_attempts."""
        self.con.execute(
            'UPDATE jobs SET status="queued" WHERE status="retryable_failed" AND attempts < max_attempts'
        )
        self.con.commit()

    def promote_due_jobs(self, now_iso: str | None = None):
        """Promote retryable_failed jobs whose backoff window has elapsed."""
        now_iso = now_iso or datetime.now(timezone.utc).isoformat()
        self.con.execute(
            'UPDATE jobs SET status="queued", not_before=NULL '
            'WHERE status="retryable_failed" AND (not_before IS NULL OR not_before <= ?)',
            (now_iso,)
        )
        self.con.commit()

    # ──────────────────────────────────────────────
    # INFERENCE METRICS
    # ──────────────────────────────────────────────

    def record_inference_metric(self, job_id: str, model: str, total_ms: float = 0,
                                 load_ms: float = 0, prompt_eval_ms: float = 0,
                                 eval_ms: float = 0, prompt_tokens: int = 0,
                                 output_tokens: int = 0, cache_hit: bool = False,
                                 success: bool = True):
        self.con.execute(
            'INSERT INTO inference_metrics (job_id, model, total_ms, load_ms, prompt_eval_ms, eval_ms, '
            'prompt_tokens, output_tokens, cache_hit, success, recorded_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
            (job_id, model, total_ms, load_ms, prompt_eval_ms, eval_ms,
             prompt_tokens, output_tokens, int(cache_hit), int(success),
             datetime.now(timezone.utc).isoformat())
        )
        self.con.commit()

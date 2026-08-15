from datetime import datetime, timezone
from .database import connect
from ..schemas import Email, EmailAnalysis, InboxBriefing
class Repository:
 def __init__(self, path): self.con=connect(path)
 def upsert_email(self, email, fingerprint):
  self.con.execute('INSERT INTO emails VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload,content_hash=excluded.content_hash,imported_at=excluded.imported_at',(email.id,email.model_dump_json(),fingerprint,datetime.now(timezone.utc).isoformat())); self.con.commit()
 def emails(self): return [Email.model_validate_json(r['payload']) for r in self.con.execute('SELECT payload FROM emails ORDER BY imported_at DESC')]
 def email(self, email_id):
  r=self.con.execute('SELECT payload FROM emails WHERE id=?',(email_id,)).fetchone(); return Email.model_validate_json(r['payload']) if r else None
 def cached_analysis(self, email_id, fingerprint, model, schema='1'):
  r=self.con.execute('SELECT payload FROM email_analysis WHERE email_id=? AND content_hash=? AND model_name=? AND schema_version=?',(email_id,fingerprint,model,schema)).fetchone(); return EmailAnalysis.model_validate_json(r['payload']) if r else None
 def save_analysis(self, email_id, fingerprint, model, analysis, schema='1'):
  self.con.execute('INSERT INTO email_analysis VALUES(?,?,?,?,?,?) ON CONFLICT(email_id) DO UPDATE SET content_hash=excluded.content_hash,model_name=excluded.model_name,schema_version=excluded.schema_version,payload=excluded.payload,analyzed_at=excluded.analyzed_at',(email_id,fingerprint,model,schema,analysis.model_dump_json(),datetime.now(timezone.utc).isoformat())); self.con.commit()
 def cached_briefing(self, fingerprint, model, schema='1'):
  row=self.con.execute('SELECT payload FROM inbox_briefing WHERE fingerprint=? AND model_name=? AND schema_version=?',(fingerprint,model,schema)).fetchone()
  return InboxBriefing.model_validate_json(row['payload']) if row else None
 def save_briefing(self, fingerprint, model, briefing, schema='1'):
  self.con.execute('INSERT INTO inbox_briefing VALUES(?,?,?,?,?) ON CONFLICT(fingerprint) DO UPDATE SET model_name=excluded.model_name,schema_version=excluded.schema_version,payload=excluded.payload,generated_at=excluded.generated_at',(fingerprint,model,schema,briefing.model_dump_json(),datetime.now(timezone.utc).isoformat())); self.con.commit()

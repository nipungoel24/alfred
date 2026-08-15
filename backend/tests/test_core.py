from pathlib import Path
from backend.app.schemas import Email, EmailAnalysis, Category, Priority
from backend.app.mail.fingerprint import content_fingerprint
from backend.app.db.repositories import Repository
from backend.app.mail.normalizer import normalized_email
from backend.app.mail.briefing_fingerprint import briefing_fingerprint
from backend.app.schemas import InboxBriefing

def email(body='hello'):
 return Email(id='one',sender='a@example.com',subject='A subject',body=body)
def analysis(): return EmailAnalysis(short_summary='Summary',category=Category.work,priority=Priority.high,priority_score=80,reason_for_priority='Deadline',needs_reply=True)
def test_fingerprint_is_deterministic_and_changes():
 assert content_fingerprint(email())==content_fingerprint(email())
 assert content_fingerprint(email())!=content_fingerprint(email('changed'))
def test_analysis_cache_invalidates_content_and_model(tmp_path:Path):
 repo=Repository(tmp_path/'alfred.sqlite3'); e=email(); fp=content_fingerprint(e); repo.upsert_email(e,fp); repo.save_analysis(e.id,fp,'qwen3:4b',analysis())
 assert repo.cached_analysis(e.id,fp,'qwen3:4b').short_summary=='Summary'
 assert repo.cached_analysis(e.id,content_fingerprint(email('changed')),'qwen3:4b') is None
 assert repo.cached_analysis(e.id,fp,'different') is None

def test_normalizer_treats_html_as_safe_text():
 record=normalized_email({'email_id':'x','sender_email':'a@b.com','subject':'<b>Hello</b>','body':'<script>alert(1)</script><a href="javascript:bad()">Read</a>'},0)
 assert '<script' not in record.body.lower()
 assert 'alert' not in record.body.lower()
 assert record.subject == 'Hello'

def test_briefing_cache_invalidates_when_analysis_changes(tmp_path:Path):
 repo=Repository(tmp_path/'alfred.sqlite3'); e=email(); fp=content_fingerprint(e); repo.upsert_email(e,fp); repo.save_analysis(e.id,fp,'qwen3:4b',analysis()); e.analysis=analysis()
 key=briefing_fingerprint([e],'qwen3:4b')
 briefing=InboxBriefing(executive_summary='One item',total_emails=1,urgent_count=0,high_priority_count=1,needs_reply_count=1,deadline_count=0)
 repo.save_briefing(key,'qwen3:4b',briefing)
 assert repo.cached_briefing(key,'qwen3:4b').executive_summary == 'One item'
 e.analysis.priority_score=81
 assert briefing_fingerprint([e],'qwen3:4b') != key

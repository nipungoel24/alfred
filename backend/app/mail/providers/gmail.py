import base64
import httpx
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from .base import MailProvider
from ...schemas import Email, EmailAccount
from ...mail.fingerprint import content_fingerprint

class GmailProvider(MailProvider):
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url_base = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        self.gmail_base_url = "https://gmail.googleapis.com/gmail/v1/users/me"

    async def get_auth_url(self, redirect_uri: str, state: str, code_challenge: str) -> str:
        scopes = [
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/gmail.readonly"
        ]
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes),
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }
        # Use httpx.URL to properly escape values
        query = "&".join(f"{k}={httpx.URL(v)}" for k, v in params.items())
        return f"{self.auth_url_base}?{query}"

    async def exchange_code(self, code: str, redirect_uri: str, code_verifier: str) -> Dict[str, Any]:
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
            "code_verifier": code_verifier
        }
        async with httpx.AsyncClient() as client:
            r = await client.post(self.token_url, data=data)
            r.raise_for_status()
            return r.json()

    async def refresh_tokens(self, refresh_token: str) -> Dict[str, Any]:
        data = {
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token"
        }
        async with httpx.AsyncClient() as client:
            r = await client.post(self.token_url, data=data)
            r.raise_for_status()
            return r.json()

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            r = await client.get(self.userinfo_url, headers=headers)
            r.raise_for_status()
            return r.json()

    async def refresh_message_labels(self, access_token: str, msg_id: str) -> list[str] | None:
        """Fetch ONLY the current label set of a message (format=METADATA).

        Returns None on any API error. Never transfers message bodies.
        """
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(
                    f"{self.gmail_base_url}/messages/{msg_id}",
                    headers=headers, params={"format": "METADATA"}
                )
                r.raise_for_status()
                return r.json().get("labelIds") or []
        except Exception:
            return None

    async def sync_messages(self, account: EmailAccount, credentials: Dict[str, Any], repo, load_older: bool = False) -> Dict[str, Any]:
        import json
        access_token = credentials.get("access_token")
        refresh_token = credentials.get("refresh_token")
        expires_at_str = credentials.get("expires_at")

        # Check and refresh token if expired
        is_expired = False
        if expires_at_str:
            try:
                expires_at = datetime.fromisoformat(expires_at_str)
                if datetime.now(timezone.utc) >= expires_at:
                    is_expired = True
            except ValueError:
                is_expired = True
        else:
            is_expired = True

        if is_expired and refresh_token:
            try:
                res = await self.refresh_tokens(refresh_token)
                access_token = res.get("access_token")
                expires_in = res.get("expires_in", 3600)
                new_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
                
                # Encrypt and save updated credentials
                from ...db.secure_store import encrypt_token
                enc_access = encrypt_token(access_token)
                enc_refresh = encrypt_token(refresh_token)
                repo.save_credentials(account.id, enc_refresh, enc_access, new_expires_at.isoformat())
            except Exception as e:
                # Set account status to error if refresh fails
                account.connection_status = "error"
                repo.save_account(account)
                raise e

        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Parse sync_cursor
        history_id = None
        next_page_token = None
        if account.sync_cursor:
            try:
                cursor_data = json.loads(account.sync_cursor)
                history_id = cursor_data.get("history_id")
                next_page_token = cursor_data.get("next_page_token")
            except Exception:
                # For backwards compatibility if sync_cursor is just history_id
                history_id = account.sync_cursor

        imported = 0
        skipped = 0
        label_updates = 0

        async with httpx.AsyncClient() as client:
            # Helper to fetch and upsert full details for a message ID
            async def import_message_id(msg_id):
                nonlocal imported, skipped
                if repo.email(msg_id) is not None:
                    skipped += 1
                    return
                # Fetch full message payload
                r_detail = await client.get(f"{self.gmail_base_url}/messages/{msg_id}", headers=headers)
                r_detail.raise_for_status()
                msg_detail = r_detail.json()
                normalized = self._normalize_message(msg_detail, account.id)
                repo.upsert_email(normalized, content_fingerprint(normalized))
                imported += 1

            # Helper: refresh ONLY the label set of a cached message via
            # format=METADATA (no body transfer).
            async def refresh_labels(msg_id) -> bool:
                nonlocal label_updates
                try:
                    r = await client.get(
                        f"{self.gmail_base_url}/messages/{msg_id}",
                        headers=headers, params={"format": "METADATA"}
                    )
                    r.raise_for_status()
                    labels = r.json().get("labelIds") or []
                    if repo.update_email_labels(msg_id, labels):
                        label_updates += 1
                    return True
                except Exception:
                    return False

            if load_older:
                if not next_page_token:
                    return {"imported": 0, "skipped_duplicates": 0, "message": "No older messages to load"}
                
                params = {"q": "label:INBOX", "maxResults": 50, "pageToken": next_page_token,
                          "includeSpamTrash": "false"}
                r = await client.get(f"{self.gmail_base_url}/messages", headers=headers, params=params)
                r.raise_for_status()
                res_json = r.json()
                
                messages_list = res_json.get("messages", [])
                for msg in messages_list:
                    if repo.email_exists(msg["id"]):
                        labels = msg.get("labelIds")
                        if labels:
                            repo.update_email_labels(msg["id"], labels)
                            label_updates += 1
                        skipped += 1
                        continue
                    await import_message_id(msg["id"])

                # Update next page token, keeping history_id unchanged
                new_next_page = res_json.get("nextPageToken")
                new_cursor = {
                    "history_id": history_id,
                    "next_page_token": new_next_page
                }
                account.sync_cursor = json.dumps(new_cursor)
                repo.save_account(account)
                return {"imported": imported, "skipped_duplicates": skipped,
                        "label_updates": label_updates, "has_more": bool(new_next_page)}

            # Regular Sync Flow
            run_full_sync = False
            history_records = []
            
            if history_id:
                try:
                    history_params = {"startHistoryId": history_id, "maxResults": 100}
                    next_hist_page = None
                    while True:
                        if next_hist_page:
                            history_params["pageToken"] = next_hist_page
                        r = await client.get(f"{self.gmail_base_url}/history", headers=headers, params=history_params)
                        # Let's check status directly so we can handle 404/410 specifically
                        if r.status_code in (400, 404, 410):
                            run_full_sync = True
                            break
                        r.raise_for_status()
                        res_json = r.json()
                        history_records.extend(res_json.get("history", []))
                        next_hist_page = res_json.get("nextPageToken")
                        if not next_hist_page:
                            break
                except Exception:
                    # Generic network or api failure, recover with full sync if appropriate
                    run_full_sync = True

            if not history_id or run_full_sync:
                # Perform Full Sync / Safe Recovery Sync
                # 1. Fetch current profile to get latest historyId
                r_profile = await client.get(f"https://gmail.googleapis.com/gmail/v1/users/me/profile", headers=headers)
                r_profile.raise_for_status()
                latest_history_id = r_profile.json().get("historyId")

                # 2. Fetch the first page of inbox messages.
                #    includeSpamTrash=false: normal inbox acquisition must
                #    never pull Spam/Trash into Alfred.
                params = {"q": "label:INBOX", "maxResults": 50, "includeSpamTrash": "false"}
                r = await client.get(f"{self.gmail_base_url}/messages", headers=headers, params=params)
                r.raise_for_status()
                res_json = r.json()
                
                messages_list = res_json.get("messages", [])
                for msg in messages_list:
                    if repo.email_exists(msg["id"]):
                        labels = msg.get("labelIds")
                        if labels:
                            repo.update_email_labels(msg["id"], labels)
                            label_updates += 1
                        skipped += 1
                        continue
                    await import_message_id(msg["id"])

                # 3. Store new cursor
                new_next_page = res_json.get("nextPageToken")
                new_cursor = {
                    "history_id": latest_history_id,
                    "next_page_token": new_next_page
                }
                account.sync_cursor = json.dumps(new_cursor)
                account.last_sync_at = datetime.now(timezone.utc).isoformat()
                account.connection_status = "connected"
                repo.save_account(account)
                return {"imported": imported, "skipped_duplicates": skipped,
                        "label_updates": label_updates}

            else:
                # Process incremental history changes
                new_messages = []
                deleted_messages = []
                label_changed = []  # (msg_id, has_full_label_set_in_event)
                for record in history_records:
                    # Collect added messages
                    for added in record.get("messagesAdded", []):
                        msg = added.get("message", {})
                        if msg.get("id"):
                            new_messages.append(msg)
                    # Collect deleted messages
                    for deleted in record.get("messagesDeleted", []):
                        msg = deleted.get("message", {})
                        if msg.get("id"):
                            deleted_messages.append(msg["id"])
                    # Label mutations
                    for changed in record.get("labelsAdded", []):
                        msg = changed.get("message", {})
                        if msg.get("id"):
                            label_changed.append(msg)
                    for changed in record.get("labelsRemoved", []):
                        msg = changed.get("message", {})
                        if msg.get("id"):
                            label_changed.append(msg)

                # Remove duplicates from our local list
                new_ids = list(dict.fromkeys(m.get("id") for m in new_messages))
                deleted_ids = list(dict.fromkeys(deleted_messages))
                label_changed_ids = list(dict.fromkeys(
                    m.get("id") for m in label_changed
                    if isinstance(m, dict) and m.get("id")
                ))

                # Track messages already handled so refresh skips them
                handled_ids = set()

                for msg in new_messages:
                    msg_id = msg["id"]
                    handled_ids.add(msg_id)
                    labels = set(msg.get("labelIds") or [])
                    if repo.email_exists(msg_id):
                        # Cached: refresh full label set via metadata
                        await refresh_labels(msg_id)
                        continue
                    # Uncached: import only if it is (now) an active inbox
                    # message and not spam/trash. History-added spam stays
                    # out of Alfred entirely.
                    if "INBOX" in labels and "SPAM" not in labels and "TRASH" not in labels:
                        try:
                            await import_message_id(msg_id)
                        except Exception:
                            pass  # Ignore individual message load errors
                    # else: spam/trash/archived arrivals are intentionally skipped

                for changed_id in label_changed_ids:
                    if changed_id in handled_ids or not repo.email_exists(changed_id):
                        continue
                    await refresh_labels(changed_id)

                # Permanently-deleted messages: retain source row for
                # history/thread integrity but exclude from Alfred entirely.
                for msg_id in deleted_ids:
                    if repo.email_exists(msg_id):
                        repo.mark_email_excluded(msg_id)

                # Get latest historyId from profile
                r_profile = await client.get(f"https://gmail.googleapis.com/gmail/v1/users/me/profile", headers=headers)
                r_profile.raise_for_status()
                latest_history_id = r_profile.json().get("historyId")

                new_cursor = {
                    "history_id": latest_history_id,
                    "next_page_token": next_page_token # Keep next_page_token for loading older messages intact
                }
                account.sync_cursor = json.dumps(new_cursor)
                account.last_sync_at = datetime.now(timezone.utc).isoformat()
                account.connection_status = "connected"
                repo.save_account(account)
                return {"imported": imported, "skipped_duplicates": skipped,
                        "label_updates": label_updates}

    def _normalize_message(self, detail: Dict[str, Any], account_id: str) -> Email:
        headers = detail.get("payload", {}).get("headers", [])
        
        headers_dict = {}
        for h in headers:
            headers_dict[h.get("name", "").lower()] = h.get("value", "")

        sender_raw = headers_dict.get("from", "")
        sender_email = sender_raw
        sender_name = None
        
        # Parse "Name <email@domain.com>" format
        if "<" in sender_raw and ">" in sender_raw:
            parts = sender_raw.split("<")
            sender_name = parts[0].strip(' "\'')
            sender_email = parts[1].strip("> ")

        recipients_raw = headers_dict.get("to", "")
        recipients = [r.strip() for r in recipients_raw.split(",") if r.strip()]

        subject = headers_dict.get("subject", "(No Subject)")
        body = self._extract_body(detail.get("payload", {}))
        
        received_ms = int(detail.get("internalDate", 0))
        received_at = datetime.fromtimestamp(received_ms / 1000.0, timezone.utc)

        label_ids = [str(l) for l in detail.get("labelIds", []) or []]

        # Lean metadata only — the full raw payload (with base64 bodies) is
        # never persisted twice.
        snippet = detail.get("snippet", "") or ""
        raw_meta = {
            "labelIds": label_ids,
            "internalDate": detail.get("internalDate"),
            "sizeEstimate": detail.get("sizeEstimate"),
            "snippet": snippet[:500],
        }

        return Email(
            id=detail.get("id"),
            thread_id=detail.get("threadId"),
            account_id=account_id,
            sender=sender_email,
            sender_name=sender_name,
            recipients=recipients,
            subject=subject,
            body=body,
            received_at=received_at,
            label_ids=label_ids,
            source_metadata={"gmail_raw": raw_meta}
        )

    def _clean_html(self, html: str) -> str:
        import re
        from html import unescape
        # Strip script and style blocks
        text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.I | re.S)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.I | re.S)
        # Convert line breaks and block ends to newlines
        text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
        text = re.sub(r"</p>", "\n\n", text, flags=re.I)
        text = re.sub(r"</div>", "\n", text, flags=re.I)
        text = re.sub(r"</h1>|</h2>|</h3>", "\n\n", text, flags=re.I)
        # Remove remaining tags and unescape HTML symbols
        text = re.sub(r"<[^>]+>", " ", text)
        text = unescape(text)
        # Strip whitespace from each line while maintaining structure
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
        return "\n".join(lines).strip()

    def _extract_body(self, payload: Dict[str, Any]) -> str:
        if "parts" in payload:
            text_body = ""
            html_body = ""
            for part in payload["parts"]:
                mime_type = part.get("mimeType", "")
                body_data = part.get("body", {}).get("data", "")
                if mime_type == "text/plain" and body_data:
                    text_body += base64.urlsafe_b64decode(body_data.encode("ascii")).decode("utf-8", errors="replace")
                elif mime_type == "text/html" and body_data:
                    html_body += base64.urlsafe_b64decode(body_data.encode("ascii")).decode("utf-8", errors="replace")
                elif "parts" in part:
                    sub_body = self._extract_body(part)
                    if sub_body:
                        text_body += sub_body
            if text_body:
                return text_body
            if html_body:
                return self._clean_html(html_body)
            return ""
        else:
            body_data = payload.get("body", {}).get("data", "")
            mime_type = payload.get("mimeType", "")
            if body_data:
                decoded = base64.urlsafe_b64decode(body_data.encode("ascii")).decode("utf-8", errors="replace")
                if mime_type == "text/html":
                    return self._clean_html(decoded)
                return decoded
        return ""

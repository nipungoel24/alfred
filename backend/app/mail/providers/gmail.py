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

    async def get_auth_url(self, redirect_uri: str) -> str:
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
            "prompt": "consent"
        }
        query = "&".join(f"{k}={httpx.URL(v)}" for k, v in params.items())
        return f"{self.auth_url_base}?{query}"

    async def exchange_code(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
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

    async def sync_messages(self, account: EmailAccount, credentials: Dict[str, Any], repo) -> Dict[str, Any]:
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

        # Perform sync using Gmail API
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Build query for sync: last 7 days if initial, or after last sync
        if account.last_sync_at:
            try:
                last_dt = datetime.fromisoformat(account.last_sync_at)
                epoch = int(last_dt.timestamp())
                q = f"after:{epoch}"
            except Exception:
                # Fallback to 7 days
                days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y/%m/%d")
                q = f"after:{days_ago}"
        else:
            days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y/%m/%d")
            q = f"after:{days_ago}"

        params = {"q": q, "maxResults": 50}
        messages_list = []
        
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.gmail_base_url}/messages", headers=headers, params=params)
            r.raise_for_status()
            res_json = r.json()
            messages_list = res_json.get("messages", [])

            imported = 0
            skipped = 0

            for msg_summary in messages_list:
                msg_id = msg_summary.get("id")
                
                # Deduplication check
                if repo.email(msg_id) is not None:
                    skipped += 1
                    continue
                
                # Fetch full message
                r_detail = await client.get(f"{self.gmail_base_url}/messages/{msg_id}", headers=headers)
                r_detail.raise_for_status()
                msg_detail = r_detail.json()
                
                normalized = self._normalize_message(msg_detail, account.id)
                repo.upsert_email(normalized, content_fingerprint(normalized))
                imported += 1

            # Update sync status
            account.last_sync_at = datetime.now(timezone.utc).isoformat()
            account.connection_status = "connected"
            repo.save_account(account)

            return {"imported": imported, "skipped_duplicates": skipped}

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
            source_metadata={"gmail_raw": detail}
        )

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
            return text_body if text_body else html_body
        else:
            body_data = payload.get("body", {}).get("data", "")
            if body_data:
                return base64.urlsafe_b64decode(body_data.encode("ascii")).decode("utf-8", errors="replace")
        return ""

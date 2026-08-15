from typing import List, Dict, Any
from ....schemas import Email, EmailAccount

class MailProvider:
    async def get_auth_url(self, redirect_uri: str) -> str:
        """Returns the authorization URL to start the OAuth flow."""
        raise NotImplementedError

    async def exchange_code(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchanges authorization code for access and refresh tokens."""
        raise NotImplementedError

    async def refresh_tokens(self, refresh_token: str) -> Dict[str, Any]:
        """Uses refresh token to get a new access token."""
        raise NotImplementedError

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Retrieves user account info (email, name)."""
        raise NotImplementedError

    async def sync_messages(self, account: EmailAccount, credentials: Dict[str, Any], repo) -> Dict[str, Any]:
        """Synchronizes mailbox messages and returns counts."""
        raise NotImplementedError

    async def send_draft_reply(self, account: EmailAccount, credentials: Dict[str, Any], original_email: Email, reply_body: str) -> Dict[str, Any]:
        """Sends a reply to an existing email thread."""
        raise NotImplementedError

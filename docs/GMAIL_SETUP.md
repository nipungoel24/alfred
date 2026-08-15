# Alfred Gmail Developer Setup & Privacy Guide

This document details how to configure a Google Cloud Project to connect your Gmail account to Alfred, and outlines how your privacy is guaranteed locally on your device.

---

## 1. Google Cloud Console Setup (OAuth 2.0 Credentials)

To connect Gmail to Alfred, you must create a Developer Project on Google Cloud. This allows Alfred to sync your emails locally using the official Gmail API.

### Step 1: Create a Google Cloud Project
1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project dropdown in the top bar, then click **New Project**.
3. Name your project (e.g., `Alfred Smart Inbox`) and click **Create**.

### Step 2: Enable the Gmail API
1. Navigate to **APIs & Services > Library** via the left sidebar.
2. Search for `Gmail API`.
3. Select the **Gmail API** card and click **Enable**.

### Step 3: Configure the OAuth Consent Screen
1. Navigate to **APIs & Services > OAuth consent screen**.
2. Select **External** (or Internal if you are within a Google Workspace domain) and click **Create**.
3. Fill in the required fields:
   * **App name**: `Alfred`
   * **User support email**: Your email address
   * **Developer contact information**: Your email address
4. Click **Save and Continue**.
5. **Scopes (Crucial)**: Click **Add or Remove Scopes** and select:
   * `.../auth/userinfo.email` (Read email address to identify accounts)
   * `.../auth/gmail.readonly` (Read message details for local sync)
6. **Test Users**: Under the "Test users" tab, click **Add Users** and add the Gmail address you intend to sync. Google restricts OAuth logins to these test accounts before the app is published.

### Step 4: Create OAuth 2.0 Client Credentials
1. Navigate to **APIs & Services > Credentials**.
2. Click **Create Credentials** at the top, then select **OAuth client ID**.
3. Set the **Application type** to **Desktop app** (Installed application).
4. Set the **Name** to `Alfred Desktop Client`.
5. Click **Create**.
6. Google will generate your **Client ID** and a **Client Secret**. (Note: For Desktop app credentials, Google dynamically permits loopback redirects on any port to `http://127.0.0.1` automatically, so you do not need to register authorized redirect URIs in the console!).
7. Copy your **Client ID** and **Client Secret**.

---

## 2. Alfred Local Configuration

Create or update the `.env` file in your repository root directory (where `backend/` and `frontend/` folders are located):

```env
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen3:4b
ALFRED_HOST=127.0.0.1
ALFRED_PORT=8765

# Gmail OAuth Credentials (obtained in Step 4 above)
GMAIL_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your_client_secret_here
```

Restart Alfred. Navigate to the **Accounts** screen in Alfred, and click **Connect Gmail Account** to start sync!

---

## 3. Security & Local-First Privacy Guarantees

Alfred is designed with a strict local-first privacy architecture:

* **No Cloud AI Fallback:** All email body text, summaries, actions, and reply drafts are parsed and generated 100% locally on your machine using Ollama. Alfred does not send any mail data to OpenAI, Anthropic, Gemini, or any third-party AI api.
* **Secure Token Storage:** OAuth refresh and access tokens are encrypted using Windows Data Protection API (DPAPI) via native OS calls. Only the currently logged-in Windows user account has permission to decrypt the credentials.
* **Malicious Input Protection (XSS & Prompt Injection):**
  * Email HTML structures are sanitized to strip out malicious scripts, event handlers, and JavaScript URLs.
  * System prompts explicitly treat email contents as untrusted data inputs, preventing prompt injections from modifying Alfred's configuration or executing unauthorized local OS commands.

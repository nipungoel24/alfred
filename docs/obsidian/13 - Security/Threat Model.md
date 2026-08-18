---
type: security
layer: security
status: active
tags:
  - security
  - architecture
---

# Threat Model

Adversaries and attacks Alfred considers, and the controls per attack. Honest about residuals.

## Assets

1. **Mail content** ([[emails]], [[email_analysis]]) — the crown jewels.
2. **OAuth tokens** ([[credentials]]) — capability to read mail forever.
3. **Local derived state** ([[tasks]], briefings) — low sensitivity, high personal value.
4. **Model availability** — the product depends on Ollama.

## Attackers & attacks

| Attacker | Attack | Control | Residual |
|---|---|---|---|
| Remote (email sender) | Prompt injection via crafted mail | Sanitization + prompt rules + no actuators ([[Prompt Injection Defense]]) | Bad analysis/task possible; user can delete |
| Remote (email sender) | HTML/JS payload | Server-side HTML strip at sync; frontend renders text only ([[Email Content Trust Boundary]]) | Low |
| Remote (network) | Access local API | Loopback bind only; CORS allowlist ([[Local API Security]]) | Local malware not covered |
| Remote (Google-adjacent phishing) | Token theft via fake popup | PKCE + one-time state ([[OAuth Security]]) | User-level phishing always possible |
| Local other-user process | Steal SQLite + tokens | DPAPI binds ciphertext to user ([[DPAPI]]) | Same-user malware defeats DPAPI |
| Local same-user malware | Read DB / call API / prompt-inject | None beyond OS | **Accepted** — local-first trust model |
| Physical attacker | Boot OS, read disk | None (no BitLocker integration) | Accepted; documented |

## The residual-risk doctrine

Alfred protects **remote** attackers and **cross-user** locals. It explicitly does not defend against same-user malware — a desktop mail client cannot. [[Security Architecture]] keeps that boundary visible instead of pretending otherwise.

## Related

- [[Trust Boundaries]]
- [[Data Privacy]]
- [[Security Architecture]]

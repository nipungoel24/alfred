---
type: security
layer: security
status: active
tags:
  - security
---

# Trust Boundaries

The explicit lines between trust domains, with what crosses each.

```mermaid
flowchart TB
    subgraph untrusted[Untrusted]
        M[Email content]
        G[Google / Gmail API]
    end
    subgraph local[Trusted local machine]
        BE[FastAPI sidecar]
        OL[Ollama]
        DB[(SQLite)]
        WV[WebView / React]
        T[Tauri]
    end
    M -->|"sanitize at sync + prompt rules"| BE
    G -->|"OAuth2+PKCE, read-only scope"| BE
    BE -->|"schema JSON, no actuators"| OL
    BE --> DB
    WV -->|"CSP: localhost only"| BE
    T -->|"spawn/own"| BE
```

## The rules per boundary

1. **Email → code**: content is data, never markup or instructions ([[Email Content Trust Boundary]]).
2. **Google → Alfred**: tokens in DPAPI, scopes minimal, state one-time ([[OAuth Security]]).
3. **Alfred → Ollama**: loopback; schema-constrained output; no tool/function-calling surface.
4. **WebView → backend**: CORS allowlist (`localhost:5173`, `tauri://localhost`), CSP connect-src ([[Local API Security]], [[Native Security]]).
5. **Backend → SQLite**: single process, single repository class ([[Database Architecture]]).

## Related

- [[Threat Model]]
- [[Security Architecture]]

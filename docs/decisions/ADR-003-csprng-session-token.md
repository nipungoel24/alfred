# ADR-003 — CSPRNG session token, constant-time comparison

Status: Accepted
Date: 2026-09-26
Gate: 0

## Context

The backend binds to `127.0.0.1` on a dynamic port. Any local process can find that port
and any local process can call the API. The only thing standing between a random local
program and a user's entire mailbox is a per-launch token, passed as
`ALFRED_RUNTIME_TOKEN` and required by `runtime_token_middleware`.

The current implementation of that token is not fit for purpose.

`desktop/src-tauri/src/main.rs:224-240`:

```rust
fn generate_token() -> String {
    let mut h = RandomState::new().build_hasher();
    h.write_u128(SystemTime::now().duration_since(UNIX_EPOCH)...as_nanos());
    h.write_u128(std::process::id() as u128);
    let a = h.finish();
    // ... second hash seeded from the first
    format!("{:016x}{:016x}", a, h2.finish())
}
```

`RandomState` is SipHash with a per-process random key. The *inputs* are wall-clock
nanoseconds, the process ID, and a monotonic clock reading. All three are observable or
guessable by any process that can read the system clock and the process table. The token
is not unpredictable, and
`docs/obsidian/14 - Decisions/ADR-015 - Desktop Session Authentication.md:22` claims it is
a "high-entropy runtime token per launch", which the code does not support.

Separately, `backend/app/main.py:566` compares the token with `!=`, which short-circuits
on the first differing byte and leaks position information.

## Decision

1. The token is 32 bytes (256 bits) from the platform CSPRNG
2. It is compared with `secrets.compare_digest` (Python) / `subtle::ConstantTimeEq`
   (Rust)
3. The Obsidian ADR-015 claim is corrected to match the implementation
4. The token is never written to any log, in any form, including a length or a prefix

## Consequences

- On Windows: use the `getrandom` syscall via a crate that wraps it, or
  `BCryptGenRandom`. Do not implement entropy collection by hand.
- In the backend: `secrets.compare_digest` on both the header and the query-string form
- The SSE path (`?token=`) is compared the same way
- The `UNAUTHENTICATED_PATHS` exemption for the OAuth callback stays, because the system
  browser cannot carry the header. It is the one unauthenticated `/api` path and it is
  scoped to the callback by exact match (`main.py:551`).

## Rejected

**Keep the current derivation and document it accurately.** Rejected: accurately
documenting a predictable token on the only boundary protecting the user's mailbox is
not an acceptable outcome. The fix is a few lines.

**Bind the backend to a random port only, with no token.** Rejected: the port is
discoverable with `netstat` in milliseconds. Port obscurity is not authentication.

**Use a named pipe or a Unix socket instead of HTTP.** Rejected: it would remove the
browser-mode development workflow and the ability for the OAuth callback to be opened in
a system browser. Worth revisiting only if the loopback threat model changes.

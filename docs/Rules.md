# Alfred — Engineering Rules

Status: active
Baseline: Gate 0, 2026-09-26

These rules are mandatory. Breaking one requires either a fix or a written, linked
justification in the same change. "It was already like that" is not a justification.

---

## 1. Engineering rules

### 1.1 Inspect before modifying
Read the implementation, its tests, and its callers before changing it. If the
behaviour you are about to change is not covered by a test, add one in the same change
or state in the gate report why not.

### 1.2 No speculative rewrites
Alfred is not a rewrite target. Prefer, in order:
1. stabilisation
2. simplification
3. consolidation
4. hardening
5. replacement of a fragile mechanism
6. removal of a legacy path

Replacing an architecture requires all six of: a written reason, the affected files, a
migration strategy, incremental implementation, regression tests, an `Architecture.md`
update, and an ADR.

### 1.3 Smallest viable change
One concern per change. A fix that also reformats, renames, and restructures is three
changes wearing a disguise, and it cannot be reviewed or reverted.

### 1.4 Preserve working behaviour
207 backend, 133 frontend, 9 tools, and 9 Rust tests pass today. They are the floor,
not the ceiling. A change that makes one of them fail must justify why that test was
wrong, in writing, in the gate report.

### 1.5 No duplicate abstractions
One way to do each thing. No second HTTP client, no second theme store, no second date
formatter, no second icon set. If a shadcn component and a hand-written component do the
same job, one of them is deleted — not both kept "for now".

### 1.6 No unnecessary dependencies
Before adding one: check whether an existing dependency solves it; evaluate maintenance,
bundle impact, security, and licence; write the decision down if it is significant. Alfred
currently ships four unused dependencies and one dead file — the bar is real.

### 1.7 No invented APIs
Do not describe an endpoint, function, or config key that does not exist. Do not write
documentation of behaviour you have not read in the code. The five documents in
`docs/obsidian/11 - Desktop/` that claim a 45-second timeout when the code uses 60 are
the canonical example of this failure.

### 1.8 No fake data
No invented metrics, no fabricated counts, no synthetic user records in a
demonstration, no placeholder text in a shipped surface. Test fixtures are allowed;
product surfaces are not.

### 1.9 No fake metrics, reviews, testimonials, or social proof
Zero tolerance. No star ratings, no customer counts, no "trusted by", no invented logos,
no stock photography presented as a real customer, no aggregate usage numbers that were
not measured. If a number appears, it came from a command that produced it.

### 1.10 No placeholder content in production
No lorem ipsum, no `TODO`, no `Coming soon`, no `FIXME`, no dead navigation items, no
links to `#`, no placeholder icons. The current placeholder icon set
(`tools/generate_icons.py` declares itself a placeholder in its own docstring) is a known
Gate 7 blocker.

### 1.11 No broken links
Every internal link, route, anchor, and asset reference must resolve. As of Gate 0,
`frontend/index.html:8` references `/icon-192.png`, which does not exist. Broken
references are release blockers, not cosmetic issues.

### 1.12 No console errors
Production browser and app consoles must contain no unexpected errors, uncaught
exceptions, rejected promises, hydration errors, missing keys, missing assets, or failed
requests. As of Gate 0 the frontend test run emits a React setState-during-render
warning from `MailWorkspace` — a real defect, tracked as F20.

### 1.13 No ignored failing tests
No `xfail`, no `skip` without a linked issue, no `.only`. A test that cannot pass is
deleted or fixed, and the deletion is explained.

### 1.14 No disabled lint rules without justification
Alfred's ESLint config is minimal today. When rules are added they run. `--max-warnings=0`
stays.

### 1.15 No silent failures
An operation that can fail must either succeed observably or fail loudly. Alfred's
current silent degradations, all of which must be fixed:

| Location | Silent behaviour |
| --- | --- |
| `db/secure_store.py:41-44` | DPAPI failure falls back to reversible base64, no log |
| `db/database.py:327-330` | Unique-index creation failure loses the invariant, logs only |
| `db/database.py:401-402` | Migration backfill wrapped in bare `except: pass` |
| `ai/ollama_client.py:77-78` | Preload failure swallowed entirely |
| `ai/supervisor.py:119-120` | Subscriber callback exceptions swallowed |
| `desktop/src-tauri/src/main.rs:510` | `try_lock` failure skips backend shutdown |
| `desktop/src-tauri/src/main.rs:214` | Every log-write failure discarded with `let _ =` |
| `backend/app/config.py:19-20` | dotenv parse failure swallowed |

### 1.16 No broad exception swallowing
`except Exception: pass` is banned in `backend/app/` and `backend/sidecar.py`. Catch the
specific exception you can handle. If you truly must catch broadly, log at error level
with context and re-raise or translate to a typed error.

### 1.17 Never claim what you have not verified
"Tests pass" requires a command and a count. "Production ready" requires a gate report.
"No obvious problems" is not evidence. If a check could not be run, say so and say why.

---

## 2. UI rules

### 2.1 Banned by default

| Banned | Reason |
| --- | --- |
| Purple / violet gradients as brand or accent | Alfred's current accent is violet (`#6d5ae0` / `#8b7bf5`) and the surfaces layer adds `orb-violet`. This is the single most AI-generated-looking decision in the product and is reconsidered in `docs/Design.md` §3. |
| Generic AI gradients, aurora blobs, "glow" | `surfaces.css` currently ships four blurred drifting orbs behind the whole app. |
| Giant rounded containers everywhere | Radii must be earned by content density. |
| Excessive pill controls | A pill per option reads as a pricing page, not a tool. |
| Fake glassmorphism | Blur without a real translucent layer behind it is decoration. |
| Emoji as product icons | Zero emoji icons. Currently holds — all icons are Lucide. |
| Cursor gimmicks, custom cursors, magnetic hover | — |
| Fake reviews, counters, testimonials | §1.9 |
| AI slop imagery, generated stock "teams" | — |
| Vague marketing claims | — |
| Excessive scroll effects, parallax | — |
| Animation used to fill empty space | Motion must report state, not fill a layout. |
| Template hero sections | The website must not look like a landing-page template. |

### 2.2 Required

| Required | Current state |
| --- | --- |
| Restrained hierarchy | Mostly holds; the 2 567-line stylesheet has no documented hierarchy rule. |
| Editorial spacing | Spacing scale exists (`--space-1..10`) but is applied ad hoc. |
| Precise typography | A real 8-step scale exists in `tokens.css:33-49`. Good. Keep it. |
| Meaningful iconography | Lucide only, one library. Good. Keep it. |
| Subtle motion | Five motion tokens, all zeroed under `prefers-reduced-motion`. Good. |
| Clear states | Every interactive element needs hover, focus-visible, active, disabled, and loading. |
| Accessible controls | Real semantic elements; ARIA only to fill genuine gaps. |
| Strong alignment | One grid. Currently 4 `ambient-orb` elements break it. |
| Real product screenshots | None exist. Blocked on a working build. |
| Real photography only when available | Do not generate fake people. |

### 2.3 Reference sources
Morph Icons, TheSVG, shadcn/ui patterns, `ibelick/ui-skills`, and
`emilkowalski/skills` are **reference material for judgement**, not a mandate to install
five icon systems. Alfred ships one icon library (Lucide) and must not gain a second for
an equivalent concept. Any new icon dependency requires an ADR.

### 2.4 Every interactive state is designed
No default browser control where a product component belongs. No unstyled `<select>`,
`<button>`, or `<input>` left visible. Native semantics are correct; native *appearance*
is not acceptable in the product surface.

---

## 3. Iconography

- One icon system. Currently Lucide, used consistently across 30+ components.
- No emoji. Holds today.
- Every icon communicates a real action or state. No decorative icons.
- Icon-only controls require an accessible name (`aria-label`), not just `title`.
  `MessageReader.tsx` and `MessageRow.tsx` currently use `title` in several places.
- Brand marks are a separate concern: app icon, installer icon, splash, monochrome mark,
  favicon, OG image. All are placeholders or missing at Gate 0.

---

## 4. Motion

Motion must communicate state, preserve hierarchy, avoid distraction, and respect
`prefers-reduced-motion`. It must never disguise latency — a spinner that hides a slow
query is worse than an honest empty state.

Alfred's existing motion tokens (`110ms` micro, `150ms` hover, `220ms` pane, `300ms`
reveal, `420ms` spring) and the global reduced-motion kill-switch are good and are
preserved. The `drift-a/b/c` ambient orb animations at 110-140 s are decoration and are
removed in Phase 3.

---

## 5. Error handling

Three layers, always:

1. **User-facing message** — plain, specific, actionable. Never an exception string.
2. **Diagnostic context** — a stable machine-readable code, e.g. `BACKEND_HEALTH_TIMEOUT`.
3. **Structured log** — timestamp, subsystem, event, code, severity, correlation id.

Never show a raw traceback or a Rust error string as the primary experience. Never
swallow an error that affects correctness. Alfred's `StartupGate` currently violates both
halves of rule 1; that is fixed in Phase 1.

---

## 6. Logging

Every serious failure logs: timestamp, subsystem, event, diagnostic code, severity, and
a correlation id where one applies.

Never log: Gmail message bodies, OAuth secrets, access or refresh tokens, or private user
data. Alfred satisfies the prohibition today — this must not regress.

---

## 7. Security

- Least privilege by default. Tauri capabilities are an allowlist; a permission is added
  only with a stated need. Alfred's current `core:default` + `opener:default` with **no**
  `shell:` grant is the model to preserve.
- Tokens come from a CSPRNG. Alfred violates this today (`main.rs:224-240`).
- Secret comparison is constant-time. Alfred violates this today (`main.py:566`).
- Cryptographic failure is loud, never a downgrade. Alfred violates this today
  (`secure_store.py`).
- `postMessage` handlers verify `event.origin`. Alfred violates this today.
- Production CSP contains no development origin. Alfred violates this today.
- Secrets are never compiled into a distributed binary. Alfred violates this today
  (`build_sidecar.py` embeds the OAuth client secret).

---

## 8. Dependencies

Before adding a dependency, answer all six questions and record the answers if the
dependency is significant: does something existing solve it, is it maintained, what is
the bundle or image cost, what is the security posture, what is the licence, and is the
decision worth an ADR.

---

## 9. Performance

Do not optimise prematurely. Every optimisation ships with before/after evidence where
practical. Measure startup time, bundle size, render cost, and memory before and after.
Alfred's current single 375.83 kB JS chunk is a known Phase 4 item with a measured
baseline already recorded in this document's baseline section.

---

## 10. Testing

Tests are the evidence a gate is passed. A test that cannot fail is worse than no test,
because it manufactures false confidence. As of Gate 0 four frontend tests are vacuous or
misnamed (`docs/Memory.md` F21); they are fixed in Phase 3, not deleted quietly.

New behaviour ships with a test. A bug fix ships with a test that fails before the fix.

---

## 11. Documentation

- `docs/Memory.md` is updated at the end of every work session. A stale `Memory.md`
  invalidates the whole process.
- `docs/Architecture.md` is updated when the architecture changes.
- Architecture changes get an ADR in `docs/decisions/`.
- `README.md` must reflect reality. Today it correctly states that no public release
  exists; that statement must not become false without the release actually existing.
- Where an existing document contradicts the code, the code is correct by definition and
  the document is a bug.

---

## 12. Enforcement

These rules are enforced by the phase gates in `docs/Phases.md` and, from Phase 5, by CI.
Until CI exists, the rules are enforced by the gate report, and a gate report that
asserts compliance without evidence is itself a violation.

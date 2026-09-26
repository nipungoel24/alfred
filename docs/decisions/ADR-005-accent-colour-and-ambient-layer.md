# ADR-005 — Accent colour: teal, and removal of the ambient orb layer

Status: **Accepted** (was: Proposed — resolved 2026-09-26 in Phase 1)
Date: 2026-09-26
Gate: 1
Companion: `docs/UI-DESIGN-SPEC.md` §3.3, §3.5

## Context

Alfred's only chromatic identity was violet: `--accent #6d5ae0` (light), `#8b7bf5`
(dark), hue 248.5°, with derived `--accent-hover`, `--accent-active`, `--accent-text`,
`--accent-soft`, `--shadow-accent`, `--border-focus` and `--unread-dot`.

Behind the whole application, `App.tsx:119-123` rendered four blurred "ambient orbs"
(violet, indigo, cyan, pink) sized in `vw`, `filter: blur(110px)`, drifting on 110–140
second loops, with six `glass-*` `backdrop-filter` surfaces layered over them.

`docs/Rules.md` §2.1 bans purple gradients, generic AI gradients and decoration that does
not earn its place. Phase 1 was required to resolve this on measurement, not preference.

## Two separable decisions

Change 1 (orb layer) and Change 2 (accent hue) are independent. Change 1 is not optional.
Change 2 was genuinely open.

---

## Change 1 — Remove the ambient orb layer. **Settled.**

Delete `.ambient-layer` / `.ambient-orb` from `surfaces.css`, the markup in `App.tsx`,
and the `drift-a/b/c` keyframes. Reduce the six `glass-*` tokens to two real surfaces
(`--bg-panel`, `--bg-elevated`).

Rationale, not preference:

- It is decorative motion with no state meaning. `docs/Rules.md` §4 requires motion to
  report state.
- `filter: blur(110px)` on a full-viewport layer is a continuous compositing cost behind
  a *reading* application.
- Once nothing moves behind them, `backdrop-filter` on six surfaces buys nothing and
  still costs a compositing layer per surface.
- Violet-orbs-over-glass is the single most recognisable signature of a generated
  interface, and Alfred's credibility rests on looking considered.

This happens regardless of the accent decision.

---

## Change 2 — Accent hue. **Measured, then decided: teal.**

### Measurement

WCAG 2.1 relative luminance, computed against the three real surfaces each mode uses.

**Candidate A — violet (current)**

| | Worst surface | Ratio | vs 4.5 |
| --- | --- | --- | --- |
| `#6d5ae0` accent light | `#f2f3f8` (`--bg-app`) | 4.52 | **+0.02** |
| `#5a49d0` accent-text | `#f2f3f8` | 5.75 | +1.25 |
| `#8b7bf5` accent dark | `#151a24` (`--bg-reader`) | 5.19 | +0.69 |

**Candidate B — teal**

| | Worst surface | Ratio | vs 4.5 |
| --- | --- | --- | --- |
| `#0b6b6b` accent light | `#f2f3f8` | 5.69 | **+1.19** |
| `#0b6b6b` accent-text | `#f2f3f8` | 5.69 | +1.19 |
| `#3fb8b0` accent dark | `#151a24` | 7.21 | +2.71 |

**Semantic colours, both modes** (corrected per `docs/Design.md` §3.2) — all pass 4.5:
success 4.62, warning 5.09, danger 4.56, info 4.59 (light); 6.79–9.52 (dark).

**Hue separation from semantics** — this is where teal is *worse*:

| Colour | Hue |
| --- | --- |
| teal accent | 180° |
| success | 160° |
| info | 211° |
| violet accent | 248.5° |
| danger | 0° |

Teal sits **20°** from success-green. Violet sits 88° from success and 38° from info.

### Decision

**Teal** (`#0b6b6b` light, `#3fb8b0` dark).

Deciding factors, in order:

1. **Violet's contrast headroom is effectively zero.** 4.52 against a 4.5 requirement is
   +0.02. Any future token adjustment — a new surface, a slightly different app
   background, a dark-mode tweak — pushes it under AA. A palette that sits exactly on
   the threshold is a latent defect, and this product has to survive token edits.
   Teal's +1.19 is a real margin.
2. **Accent is the most-used colour in the interface.** It carries selected rows, focus
   rings, the unread bar, active navigation and primary buttons. It is not a rare accent.
   The most-used colour should not be the one with no headroom.
3. **Calmer, more instrument-like.** Teal reads as equipment. Violet reads as a default.
4. **No gradient is used to compensate.** The teal palette is flat. Contrast comes from
   the value step, not from a gradient overlay.

### The trade-off, stated honestly

Teal is only 20° from success-green in hue. That is a real weakness and it is handled by
a rule rather than by pretending it does not exist:

> **Accent is never a status colour.** If something is coloured `--accent`, it means
> selected, focused, unread, or primary action. Connection and health use the semantic
> ramp. Status is always icon + accessible label, never colour alone.

Enforced in `docs/UI-DESIGN-SPEC.md` §3.5, which requires three simultaneous signals for
unread (left bar, font weight, screen-reader text) and forbids a bare coloured status
dot. With that rule in force, the two colours never have to be told apart by hue.

If teal's proximity to green later proves confusing in practice, the correct fix is to
shift the success ramp toward a distinctly different green or to rely on the icon, not to
re-pick the accent on aesthetics.

### Consequences

- Six AA failures in the light palette are corrected at the same time
  (`docs/Design.md` §3.2): `--text-muted #646c80`, `--success #0f7d59`,
  `--warning #8a5f0e`, `--info #1f6fc4`, `--danger #c53f3f`.
- `--text-faint` is redefined as **decoration only**; a "faint" text colour cannot pass
  4.5:1 and reading it as a text token is what caused the failure.
- `--shadow-accent` is removed. No coloured shadows.
- Selection becomes `inset 3px 0 0 var(--accent)` plus an 8% accent tint, so selection
  is legible without relying on the hue.
- No test asserts a colour value, so no test churn.

## The alternative, recorded

**Keep violet.** Legitimate and defensible: it passes AA today, and Alfred's brand was
never formally decided. It is rejected on the +0.02 headroom argument, not on taste. If
the owner overrules this, amend the numbers in `docs/UI-DESIGN-SPEC.md` §3.3, keep every
other change, and the product is still correct — the orb removal, the AA corrections and
the `--text-faint` restriction are independent of the hue.

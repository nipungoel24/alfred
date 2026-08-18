---
type: architecture
layer: frontend
status: active
tags:
  - frontend
  - architecture
---

# Design System

The token-driven visual language: Mattered-style structure, Siri-like ambient energy, Apple-grade restraint.

## File layout (`frontend/src/styles/`)

| File | Owns |
|---|---|
| `tokens.css` | scales: motion, radii (2/4/6/10/14), spacing, type (11.5–27px), layout widths, blur, z-scale |
| `themes.css` | complete light/dark color systems: semantic colors, reader surfaces, glass, elevation, ambient aurora |
| `motion.css` | every keyframe + reveal utilities + `prefers-reduced-motion` kill-switch |
| `surfaces.css` | aurora background system, glass vocabulary, elevation helpers, accent wash |
| `globals.css` | components: shell, rail, header, mail workspace, reader document, intelligence pane, buttons, badges, states |
| `reset.css` | base reset + token scrollbars |

## Core ideas

- **Semantic tokens only** — no component hex values; themes are complete swaps via `[data-theme]`.
- **The document is the hero** — reader renders as a `reader-surface` card (light: warm paper `#fdfdfc`; dark: elevated graphite `#151a24`) floating on the aurora, so long-form text never sits on decoration.
- **Disciplined glass** — blur only on fixed/sticky surfaces (rail, header, toolbar, floating intelligence pane); never on scrolling rows/content.
- **Motion budget** — 110ms micro, 150ms hover, 220ms pane, 300ms reveal; transform/opacity only; everything dies under reduced-motion.
- **Aurora** — four blurred orbs drifting over 110–140s at ~0.5 opacity; ambient, never under text.

## State vocabulary

Buttons (primary gradient / surface / ghost / danger), badges, glass panels, accent wash (briefing), skeletons mirroring final layout, scoped error banners, inset focus rings in overflow lists.

## Related

- [[Frontend Overview]]
- [[Application Shell]]
- [[ADR-010 - React Query]]

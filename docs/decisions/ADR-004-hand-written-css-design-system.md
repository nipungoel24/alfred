# ADR-004 — Hand-written CSS is the design system; remove the Tailwind/shadcn preflight

Status: Accepted
Date: 2026-09-26
Gate: 0

## Context

The frontend's dependency list and its actual code disagree.

Present in configuration:
- `@tailwindcss/vite` in `vite.config.ts`
- `tailwindcss` in both dependencies and devDependencies
- `@import "tailwindcss"` at `styles.css:1`
- A `@theme inline` block at `styles.css:4-41` mapping 38 shadcn colour names
- `components.json` declaring a shadcn `new-york` setup with `cssVariables: true`
- `class-variance-authority`, `clsx`, `tailwind-merge` as dependencies
- `src/lib/utils.ts` exporting `cn()` = `twMerge(clsx(...))`

Present in code:
- **Zero Tailwind utility classes.** Every `className` in every non-test file is a
  hand-written semantic name: `app-shell`, `message-row`, `intelligence-pane`,
  `startup-gate`, and roughly 200 more.
- **Zero shadcn components.** `src/components/ui/` contains exactly one file,
  `AnalysisProgress.tsx`, which is not a shadcn component.
- `cn()` is imported by nothing. `cva(` has zero call sites. `clsx` and `tailwind-merge`
  are reachable only through the dead `cn()`.
- `sharp` and `png-to-ico` are devDependencies with zero references anywhere; the brand
  script uses `System.Drawing` instead.
- `styles.css:7,9` map `--color-card` and `--color-popover` to `var(--bg-elevated)`,
  and `--bg-elevated` is defined in no stylesheet. Both resolve to nothing.

The concrete cost of the half-commitment:
- Tailwind's preflight is injected, then overridden by `src/styles/reset.css`, which does
  its own `*` margin/padding reset and its own `button` and `input` normalisation. Two
  resets fight each other on every load.
- Six dependencies exist to serve a code path nothing uses.
- A future contributor reasonably concludes that `components.json` means shadcn is in
  use, and adds `bg-background` classes that will not work, because the `@theme` mapping
  those classes depend on points at undefined variables.

## Decision

Hand-written semantic CSS with design tokens is Alfred's styling system. It stays.

In Phase 3:
1. Remove `@import "tailwindcss"` and the `@theme inline` block
2. Remove `@tailwindcss/vite` from `vite.config.ts`
3. Remove `tailwindcss`, `@tailwindcss/vite`, `class-variance-authority`, `clsx`,
   `tailwind-merge`, `sharp`, and `png-to-ico`
4. Delete `src/lib/utils.ts`
5. Delete `components.json`, or replace it with a one-line note in `frontend/README.md`
   explaining that Alfred does not use shadcn and why
6. Keep `globals.css`, but split it by concern (see Gate 4)

## Consequences

- Bundle shrinks; the change is measurable in Gate 4
- Exactly one reset, from `reset.css`, which is already correct
- The 200-odd semantic class names stay, which is the point: they are namespaced by
  feature and they are greppable
- `docs/Design.md` is the styling contract, not `components.json`
- Adding shadcn later is possible, but it would be a deliberate new ADR, not a
  `npx shadcn add` away

## Rejected

**Adopt Tailwind properly — rewrite every className as utilities.** Rejected: it would
touch all 34 `.tsx` files and a 2 567-line stylesheet to change a mechanism that already
works. The existing CSS is coherent, token-driven, and fully covered by tests that assert
on semantic class names. This would be the speculative rewrite `docs/Rules.md` §1.2
forbids.

**Actually adopt shadcn/ui.** Rejected for now: the reference set is good, but adopting a
component library means either Tailwind or a CSS-variable adapter, plus a Radix
dependency, plus learning a new component API — all to fix problems Alfred does not
currently have. The specific gaps (a shared Dialog with a focus trap, a Toast, a Tooltip)
are better solved by a small purpose-built primitive set, which is what Phase 3
considers. Revisit if the primitive set grows past roughly eight components.

**Leave the configuration and simply stop using it.** Rejected: this is the current state.
It is a permanent source of confusion and a permanent source of dead dependencies.

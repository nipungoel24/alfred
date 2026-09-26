# ADR-009 — The public website lives in a separate repository

Status: **Proposed — needs owner sign-off**
Date: 2026-09-26
Gate: 0

## Context

`docs/Phases.md` Gate 6 requires a public website with fifteen routes, per-page SEO
metadata, structured data, social images, a sitemap, and analytics. None of it exists.
Verified: no site framework config anywhere in the tree, no site directory, zero tracked
YAML files, and the only frontend is the application itself.

The website therefore has to be built from nothing, and the first real decision is where
it lives.

## Decision

The website is a **separate repository**.

The application repository stays exactly one thing: the Alfred application, its backend,
its desktop shell, its tests, and its engineering documentation.

## Rationale

1. **Different consumers.** Contributors to Alfred are contributors to a desktop
   application. A marketing site has different reviewers, different release cadence, and
   a different risk profile.
2. **Analytics isolation.** ADR-008 requires that website analytics never reach the
   application. Separate repositories make that structural rather than a review rule
   someone has to remember.
3. **Different toolchain.** The site will bring its own framework, its own lockfile, and
   its own CI. Merging that into this repository adds hundreds of megabytes of
   dependencies to a project that currently ships a 375 kB bundle.
4. **Release independence.** Publishing a blog post must never be able to fail, delay, or
   block an application release, and vice versa.
5. **The application's git history stays legible.** This repository's log tells the
   Streamlit-to-FastAPI story, the Gmail integration story, and the sidecar-lifecycle
   story. A marketing site's commits would dilute it.

## Consequences

- Screenshots for the website come from a real installed build of Alfred, so Gate 6
  genuinely depends on Gates 1 and 2. This is not a workaround; honest screenshots
  require a working application.
- `/docs` on the website links to this repository, and `/download` links to GitHub
  Releases. Both are real, stable URLs.
- The website carries the legal pages. `docs/PRD.md` §11 and `docs/Rules.md` §1.9 constrain
  what may be claimed in them.
- Two repositories means two sets of contributors and two CI bills. Accepted.

## The alternative

**`website/` inside this repository.** This is the conventional choice and it is
defensible: one clone, one issue tracker, shared design tokens, and a shared
`docs/Design.md`. It also means the application repository carries a second build system,
a second dependency tree, an analytics tag, and a deployment pipeline — none of which
have anything to do with a Gmail client.

If the owner prefers a single repository, the requirements are the same either way: the
site is a separate workspace with its own `package.json`, its own lockfile, and its own CI
job, and ADR-008's isolation requirement still applies and must be verified in the
shipped bundle.

## Blocking decision

Phase 6 does not begin until this is settled. The `/case-studies` page additionally
cannot ship without real customers — see `docs/Phases.md` Gate 6.

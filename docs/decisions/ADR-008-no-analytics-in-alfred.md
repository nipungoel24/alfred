# ADR-008 — No analytics in Alfred, under any circumstances

Status: Accepted
Date: 2026-09-26
Gate: 0

## Context

`docs/Phases.md` Gate 6 requires Google Analytics on the public website. The obvious
engineering risk is that website infrastructure bleeds into the application: a shared
bundle, a shared cookie, a shared tag manager, a shared request path.

Alfred's entire value proposition rests on a claim a user has to be able to verify: mail
content and derived intelligence are processed on their own machine and are not
transmitted anywhere except to Google's Gmail API. A single analytics beacon in the
desktop app would not just be a policy violation — it would make the product's central
claim false, and it would be invisible to the user.

## Decision

1. **Alfred contains no analytics code, no telemetry, no crash reporting, and no
   usage counting.** Not "no PII" — none. This is an architectural boundary, not a
   privacy policy.
2. **The website's analytics must never be present in the application bundle.** Verified
   by inspecting `frontend/dist` for any analytics host, and by keeping the website in a
   separate repository (ADR-009) so it cannot be accidentally merged in.
3. **The website's analytics must never receive mail-derived data.** The website has no
   access to any of it; the two systems share nothing.
4. **Any future telemetry requires a new ADR and a visible change to the privacy page.**
   It is not a small decision that can be made inside a feature branch.
5. **The privacy page states this positively and specifically**, including what Alfred
   *does* send: Gmail API requests, and nothing else.

## Consequences

- There is no "anonymous usage" to offer in a privacy policy, because there is none
- Crash reports from users are manual: sanitized `desktop.log` lines attached to a GitHub
  issue, as `README.md:431` already instructs
- The absence is verifiable, which is the point. A reader can grep the repository and
  find no beacon, and that claim is checkable

## Rejected

**Anonymous, opt-out, aggregate-only telemetry inside the app.** Rejected. Alfred handles
a user's private mail. Any code path that leaves the machine is a code path a user must
trust on faith, and "anonymous" is not verifiable from the outside. The value of a
privacy claim is that it is auditable.

**A separate opt-in "help improve Alfred" setting.** Rejected. It would be the first
foot-gun in a codebase that currently has none, and `docs/Rules.md` §1.15 forbids silent
failures of exactly this kind — a telemetry switch that ships off-by-default is a
liability, not a feature.

**Analytics on the website that could identify a visitor who also uses the app.** Rejected:
the systems share no identifier. A visitor to the website is not linked to their local
install in any way.

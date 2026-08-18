---
type: architecture
layer: frontend
status: active
tags:
  - frontend
---

# Mail Workspace Screen

The landing screen and product center: [[frontend.src.mail.MailWorkspace.MailWorkspace|MailWorkspace]].

## Regions

| Region | Width | Contents |
|---|---|---|
| Mail pane | 336px | Title+count → Inbox/All Mail segmented switch → category tabs (Inbox) or kind tabs (All Mail) → backfill status → toolbar (filters, view-scoped search, Sync) → virtualized list |
| Reader | flex | Sticky toolbar + document surface ([[Email Reader Screen]]) |
| Intelligence | 336px | Floating companion pane ([[Intelligence Pane Screen]]); overlays <1440px |

## States

- **Inbox** — category tabs Primary/Promotions/Social/Updates/Forums with live counts; semantic filters All/Important/Reply/Later.
- **All Mail** — kind filters All/Received/Sent/Archived; Sent rows carry a SENT badge, archived rows an Archived badge.
- **Global search** — header search replaces the view with results across all locally synced mail; a "Searching all local mail" banner with clear button distinguishes it from the pane filter.
- **Backfill** — observed, not driven: "Syncing older mail… · 450 synced · ~1650 remaining" or "All mail synced"; pause/resume controls act on the backend job.

## Data

`emails` (scope/kind/category/search server-side), `emailCounts`, `accounts` (refetch interval for backfill status); Later set persisted in localStorage. See [[Frontend Data Fetch Flow]].

## Related

- [[Email Reader Screen]]
- [[Intelligence Pane Screen]]
- [[API Map]]

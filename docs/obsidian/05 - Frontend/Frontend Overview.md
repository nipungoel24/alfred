---
type: architecture
layer: frontend
status: active
tags:
  - frontend
  - architecture
---

# Frontend Overview

React 19 + TypeScript + Vite under `frontend/src`, token-driven CSS, TanStack Query + Virtual, lucide icons.

## The shell

[[frontend.src.App.App|App]] owns the page state and composes:

- [[frontend.src.layout.IconRail.IconRail|IconRail]] — 56px icon navigation (Overview/Mail/Tasks/Deadlines/Accounts/Settings) with tooltips, active violet marker, brand mark, labelled connection status.
- [[frontend.src.layout.WorkspaceHeader.WorkspaceHeader|WorkspaceHeader]] — glass header: page context, global search (Ctrl+K, searches All Mail), AI Ready chip, account avatar.
- [[frontend.src.components.ui.AnalysisProgress.AnalysisProgress|AnalysisProgress]] — floating SSE pill.

## The mail workspace (landing page)

[[frontend.src.mail.MailWorkspace.MailWorkspace|MailWorkspace]]: Inbox/All Mail switch → category tabs (Inbox) or kind tabs (All Mail) → virtualized [[frontend.src.mail.MessageList.MessageList|MessageList]] → [[frontend.src.mail.MessageReader.MessageReader|MessageReader]] (document surface) → [[frontend.src.intelligence.IntelligencePanel.IntelligencePanel|IntelligencePanel]] (floating companion, overlays <1440px). Backfill status is observed, never driven.

## Feature pages

Overview (command center), Tasks, Deadlines, Accounts (connect/sync/disconnect Gmail), Settings (theme + runtime info).

## Theming

`data-theme` on `<html>` resolved pre-paint; semantic tokens per theme; motion budget; aurora ambient layer — see [[Design System]].

## Tests

Vitest + Testing Library: theme behavior, workspace switching, category scopes, selection/intelligence, Later persistence, header keyboard. See [[Frontend Tests]].

## Related

- [[Frontend Architecture]]
- [[Frontend Component Map]]
- [[Frontend Data Fetch Flow]]

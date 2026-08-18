---
type: architecture
layer: product
status: active
tags:
  - system
---

# User Journeys

The three journeys that define Alfred, each mapped to the flows and screens that implement them.

## Journey 1 — First run: connect the mailbox

1. User opens Alfred → [[frontend.src.features.accounts.AccountsPage.AccountsPage|AccountsPage]] shows no accounts.
2. User clicks *Connect Gmail* → [[POST --api-accounts-gmail-connect]] → [[Gmail OAuth Flow]] (PKCE, system browser, DPAPI token storage).
3. Callback completes → account row appears → user clicks *Sync Now* → [[POST --api-accounts-{account_id}-sync]] → [[Gmail Incremental Sync Flow]] (initial = full INBOX page).
4. Backend enqueues analysis jobs for eligible mail → [[Background Analysis Job Flow]] → rows start gaining intelligence.
5. Backend starts the durable All Mail backfill on its own → [[All Mail Backfill Flow]]; the UI only observes ("Syncing older mail…").

## Journey 2 — Morning triage

1. User opens Alfred → [[frontend.src.mail.MailWorkspace.MailWorkspace|MailWorkspace]] is the landing page.
2. [[frontend.src.mail.CategoryTabs.CategoryTabs|CategoryTabs]] show live per-tab counts; user checks Primary, then Needs Reply filter.
3. Selecting a message opens [[frontend.src.mail.MessageReader.MessageReader|MessageReader]] on a document surface; [[frontend.src.intelligence.IntelligencePanel.IntelligencePanel|IntelligencePanel]] shows summary/priority/tasks/deadline.
4. If a reply is needed, *Generate Draft* → [[POST --api-emails-{email_id}-draft]] → [[backend.app.ai.service.AIService.draft_reply]] → local text draft.
5. User opens [[frontend.src.features.overview.OverviewPage.OverviewPage|Overview]] for the briefing: [[GET --api-briefing]].
6. User checks [[frontend.src.features.tasks.TasksPage.TasksPage|Tasks]] — derived projections they can complete/delete (user state wins).

## Journey 3 — The mailbox changes while Alfred is off

1. While the backend is stopped, Gmail receives mail and moves messages between labels.
2. Alfred restarts → [[Application Startup Flow]] resumes: stuck jobs reset, historyId sync catches up ([[Gmail Incremental Sync Flow]]), backfill resumes from its persisted cursor, eligibility columns are recomputed from label history events.
3. A message moved to Spam in Gmail disappears from every Alfred projection — briefing, tasks, needs-reply — without deleting its local source row ([[Data Ownership]]).

## Related

- [[Critical Execution Paths]]
- [[Product Vision]]

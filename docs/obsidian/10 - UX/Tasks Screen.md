---
type: architecture
layer: frontend
status: active
tags:
  - frontend
---

# Tasks Screen

[[frontend.src.features.tasks.TasksPage.TasksPage|TasksPage]] — the derived projection with user-state control.

- Segmented filter (pending/completed/all) with counts in the subtitle.
- Virtualized rows: gradient check toggle, title (strikethrough when done), description, due date, priority badge, delete.
- Data: [[GET --api-tasks]] (active projection — source-eligibility filtered), [[POST --api-tasks-{task_id}-toggle]], [[DELETE --api-tasks-{task_id}]].

## Semantics to remember

Rows are *reconciled* derived data: completing/deleting is user state and survives re-derivation ([[Task Derivation Flow]], [[tasks]]).

## Related

- [[Deadlines Screen]]
- [[Task Intelligence]]
- [[API Map]]

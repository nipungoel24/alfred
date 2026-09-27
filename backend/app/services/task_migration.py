"""Task Migration Service.

A thin, explicit front door for the one authoritative reconcile in
``task_derivation.reconcile_tasks_from_analyses``. It exists so an operator can
say "migrate the task table now" and get a report, without there being a second
implementation that could drift from the startup path.

The product has no way to create a task by hand - there is no task-creation
route and no UI affordance - so every row in the table is machine-derived and
reconciling one cannot destroy something the user typed.
"""

from typing import Tuple

from ..db.repositories import Repository
from .task_derivation import reconcile_tasks_from_analyses


class TaskMigrationService:
    def __init__(self, repo: Repository):
        self.repo = repo

    def run_migration(self, model: str) -> Tuple[int, int]:
        """Reconcile every task against the current derivation logic.

        Returns ``(tasks_before, tasks_after)``. See
        :func:`reconcile_tasks_from_analyses` for the per-category breakdown and
        for the preservation rules.
        """
        report = reconcile_tasks_from_analyses(self.repo, model)
        return report.before, report.after


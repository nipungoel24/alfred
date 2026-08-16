"""Task Migration Service.

Provides production-safe task derivation upgrades.
Reconciles new derivation logic against existing task state without destroying user data.
"""
from typing import List, Set, Tuple
from ..schemas import Email, EmailAnalysis, Task
from ..db.repositories import Repository
from .task_derivation import derive_tasks, DERIVATION_VERSION

class TaskMigrationService:
    def __init__(self, repo: Repository):
        self.repo = repo

    def run_migration(self, model: str) -> Tuple[int, int]:
        """Run safe task migration over existing analyses.
        
        Returns:
            (tasks_before, tasks_after)
        """
        all_existing_tasks = self.repo.tasks()
        tasks_before = len(all_existing_tasks)
        
        # Build lookup maps for reconciliation
        existing_by_fp = {getattr(t, 'fingerprint', None): t for t in all_existing_tasks if getattr(t, 'fingerprint', None)}
        
        pairs = self.repo.all_analyses_with_emails(model)
        
        new_derived_tasks: List[Task] = []
        global_fingerprints: Set[str] = set()
        
        for email, analysis in pairs:
            tasks = derive_tasks(email, analysis)
            for task in tasks:
                fp = getattr(task, 'fingerprint', None)
                if fp and fp in global_fingerprints:
                    continue
                if fp:
                    global_fingerprints.add(fp)
                new_derived_tasks.append(task)
        
        from ..db.database import transaction
        with transaction(self.repo.con) as cur:
            # 1. Update or Insert newly derived tasks
            for task in new_derived_tasks:
                fp = getattr(task, 'fingerprint', None)
                existing = existing_by_fp.get(fp) if fp else None
                if not existing:
                    # Try by ID just in case fingerprint was null in old version
                    existing = next((t for t in all_existing_tasks if t.id == task.id), None)
                
                if existing:
                    # Reconcile: Preserve user state (status, maybe id to avoid cascading issues)
                    task.id = existing.id
                    task.status = existing.status
                    task.created_at = existing.created_at
                    cur.execute(
                        '''UPDATE tasks SET title=?, description=?, due_at=?, priority=?, status=?, 
                        derivation_version=?, confidence=?, fingerprint=? WHERE id=?''',
                        (task.title, task.description, task.due_at, task.priority, task.status,
                         getattr(task, 'derivation_version', DERIVATION_VERSION),
                         getattr(task, 'confidence', 'medium'), fp, task.id)
                    )
                else:
                    # Insert new
                    cur.execute(
                        'INSERT INTO tasks (id, source_email_id, source_thread_id, title, description, due_at, priority, status, created_at, derivation_version, confidence, fingerprint) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                        (task.id, task.source_email_id, task.source_thread_id, task.title, task.description,
                         task.due_at, task.priority, task.status, task.created_at,
                         getattr(task, 'derivation_version', DERIVATION_VERSION),
                         getattr(task, 'confidence', 'medium'), fp)
                    )
            
            # 2. Mark/remove obsolete
            obsolete_tasks = [t for t in all_existing_tasks if getattr(t, 'fingerprint', None) not in global_fingerprints]
            for obs in obsolete_tasks:
                if obs.status == 'pending':
                    cur.execute('DELETE FROM tasks WHERE id=?', (obs.id,))
                else:
                    # Preserve completed/dismissed tasks
                    pass
                
        # Commit handled by context manager/connection
        
        tasks_after = len(self.repo.tasks())
        return tasks_before, tasks_after

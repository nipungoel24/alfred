import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useVirtualizer } from '@tanstack/react-virtual';
import { useEffect, useRef, useState } from 'react';
import {
  tasks as fetchTasks, toggleTask, dismissTask, patchTaskPriority,
  TASK_PRIORITIES,
} from '../../api/emails';
import type { TaskPriority } from '../../api/emails';
import { Check, Trash2, CheckSquare, Mail, ChevronDown } from 'lucide-react';
import { SourceEmailPreview } from '../../mail/SourceEmailPreview';

interface TasksPageProps {
  onOpenInMail?: (emailId: string) => void;
}

export function TasksPage({ onOpenInMail }: TasksPageProps) {
  const queryClient = useQueryClient();
  const [filter, setFilter] = useState<'pending' | 'completed' | 'all'>('pending');
  // Live-state architecture: store only the previewed task ID and derive
  // the task from the latest query data, so priority edits and toggles
  // reflect immediately without closing the preview.
  const [previewTaskId, setPreviewTaskId] = useState<string | null>(null);

  const { data: tasks = [], isLoading } = useQuery({
    queryKey: ['tasks'],
    queryFn: fetchTasks,
  });

  const previewTask = previewTaskId ? (tasks.find(t => t.id === previewTaskId) ?? null) : null;

  // A dismissed task disappears from the active query — close cleanly.
  useEffect(() => {
    if (previewTaskId && !isLoading && !previewTask) {
      setPreviewTaskId(null);
    }
  }, [previewTaskId, previewTask, isLoading]);

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['tasks'] });

  const toggleMutation = useMutation({
    mutationFn: toggleTask,
    onSuccess: invalidate,
  });

  const dismissMutation = useMutation({
    mutationFn: dismissTask,
    onSuccess: invalidate,
  });

  const priorityMutation = useMutation({
    mutationFn: ({ id, priority }: { id: string; priority: TaskPriority }) =>
      patchTaskPriority(id, priority),
    onSuccess: invalidate,
  });

  const pendingTasks = tasks.filter(t => t.status === 'pending');
  const completedTasks = tasks.filter(t => t.status === 'completed');
  const displayTasks = filter === 'pending' ? pendingTasks : filter === 'completed' ? completedTasks : tasks;

  const parentRef = useRef<HTMLDivElement>(null);
  const rowVirtualizer = useVirtualizer({
    count: displayTasks.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 60,
    overscan: 8,
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      <div className="page-head">
        <div>
          <h1 className="page-title">Tasks</h1>
          <div className="page-subtitle">{pendingTasks.length} pending · {completedTasks.length} completed</div>
        </div>
        <div style={{ display: 'flex', gap: 2, border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', background: 'var(--bg-input)' }}>
          {(['pending', 'completed', 'all'] as const).map(f => (
            <button
              key={f}
              type="button"
              className={`btn btn-sm ${filter === f ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setFilter(f)}
              aria-pressed={filter === f}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div style={{ padding: 'var(--space-4) var(--space-6)' }} aria-busy="true">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="skeleton-row">
              <div className="skeleton" style={{ width: '60%', height: 13 }} />
              <div className="skeleton" style={{ width: '30%', height: 11 }} />
            </div>
          ))}
        </div>
      ) : displayTasks.length === 0 ? (
        <div className="empty-state">
          <CheckSquare aria-hidden="true" />
          <p>{filter === 'pending' ? 'No pending tasks.' : filter === 'completed' ? 'No completed tasks.' : 'No tasks found.'}</p>
        </div>
      ) : (
        <div ref={parentRef} style={{ flex: 1, overflowY: 'auto', minHeight: 0, padding: 'var(--space-2) var(--space-6)' }}>
          <div style={{ height: rowVirtualizer.getTotalSize(), width: '100%', position: 'relative' }}>
            {rowVirtualizer.getVirtualItems().map(virtualRow => {
              const task = displayTasks[virtualRow.index];
              const isCompleted = task.status === 'completed';
              return (
                <div
                  key={task.id}
                  data-index={virtualRow.index}
                  ref={rowVirtualizer.measureElement}
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    transform: `translateY(${virtualRow.start}px)`,
                  }}
                >
                  <div className="list-row" style={{ borderBottom: virtualRow.index === displayTasks.length - 1 ? 'none' : undefined }}>
                    <button
                      type="button"
                      className={`task-checkbox ${isCompleted ? 'checked' : ''}`}
                      onClick={() => toggleMutation.mutate(task.id)}
                      disabled={toggleMutation.isPending}
                      aria-label={isCompleted ? 'Mark incomplete' : 'Mark complete'}
                    >
                      {isCompleted && <Check aria-hidden="true" />}
                    </button>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div className={`task-title ${isCompleted ? 'completed' : ''}`}>{task.title}</div>
                      {task.description && (
                        <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginTop: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {task.description}
                        </div>
                      )}
                      <div className="task-meta">
                        {task.due_at && <span style={{ color: 'var(--accent-text)' }}>Due: {task.due_at}</span>}
                        <label className="priority-edit" title="Task priority (your edit is kept)">
                          <ChevronDown size={10} aria-hidden="true" />
                          <select
                            value={task.priority ?? 'medium'}
                            onChange={e => priorityMutation.mutate({
                              id: task.id,
                              priority: e.target.value as TaskPriority,
                            })}
                            disabled={priorityMutation.isPending}
                            aria-label={`Priority for ${task.title}`}
                            className="priority-select"
                          >
                            {TASK_PRIORITIES.map(p => (
                              <option key={p} value={p}>{p}</option>
                            ))}
                          </select>
                        </label>
                      </div>
                    </div>
                    {task.source_email_id && (
                      <button
                        type="button"
                        className="icon-btn"
                        onClick={() => setPreviewTaskId(task.id)}
                        aria-label={`View source email for ${task.title}`}
                        title="View email"
                      >
                        <Mail size={14} aria-hidden="true" />
                        <span className="btn-label">View email</span>
                      </button>
                    )}
                    <button
                      type="button"
                      className="icon-btn"
                      onClick={() => dismissMutation.mutate(task.id)}
                      disabled={dismissMutation.isPending}
                      aria-label={`Not a task: dismiss ${task.title}`}
                      title="Not a task"
                    >
                      <Trash2 aria-hidden="true" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {previewTask?.source_email_id && (
        <SourceEmailPreview
          emailId={previewTask.source_email_id}
          onClose={() => setPreviewTaskId(null)}
          onOpenInMail={onOpenInMail}
          relationship={
            <div className="source-relation">
              <div className="source-relation-label">Detected task</div>
              <div className="source-relation-title">{previewTask.title}</div>
              <div className="source-relation-row">
                <span className="field-label">Priority</span>
                <select
                  value={previewTask.priority ?? 'medium'}
                  onChange={e => priorityMutation.mutate({
                    id: previewTask.id,
                    priority: e.target.value as TaskPriority,
                  })}
                  disabled={priorityMutation.isPending}
                  aria-label={`Priority for ${previewTask.title}`}
                  className="priority-select"
                >
                  {TASK_PRIORITIES.map(p => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
              </div>
              <div className="source-relation-actions">
                <button
                  type="button"
                  className="source-relation-btn"
                  onClick={() => toggleMutation.mutate(previewTask.id)}
                  disabled={toggleMutation.isPending}
                >
                  <Check size={12} aria-hidden="true" />
                  {previewTask.status === 'completed' ? 'Mark incomplete' : 'Mark complete'}
                </button>
                <button
                  type="button"
                  className="source-relation-btn danger"
                  onClick={() => dismissMutation.mutate(previewTask.id)}
                  disabled={dismissMutation.isPending}
                  title="Durably reject this derived task"
                >
                  <Trash2 size={12} aria-hidden="true" />
                  Not a task
                </button>
              </div>
            </div>
          }
        />
      )}
    </div>
  );
}
